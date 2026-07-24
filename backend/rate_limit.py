from __future__ import annotations

from dataclasses import dataclass
import hashlib
import time

try:
    from redis import Redis
except ImportError:
    Redis = None


@dataclass(frozen=True)
class RateLimitRule:
    name: str
    limit: int
    window_seconds: int


@dataclass(frozen=True)
class RateLimitResult:
    rule: RateLimitRule
    count: int
    retry_after: int
    reset_at: int

    @property
    def allowed(self):
        return self.count <= self.rule.limit

    @property
    def remaining(self):
        return max(self.rule.limit - self.count, 0)


class RateLimitBackendUnavailable(Exception):
    pass


class RateLimitExceeded(Exception):
    def __init__(self, result: RateLimitResult):
        super().__init__("Too many requests. Please try again later.")
        self.result = result


GLOBAL_API_RATE_LIMIT = RateLimitRule("api:ip", 60, 60)
LOGIN_RATE_LIMIT = RateLimitRule("auth:login:ip", 10, 5 * 60)
REGISTER_RATE_LIMIT = RateLimitRule("auth:register:ip", 5, 10 * 60)
SEND_OTP_RATE_LIMIT = RateLimitRule("auth:send-otp:email", 3, 5 * 60)
GAME_RECORD_RATE_LIMIT = RateLimitRule("game:part:user", 20, 60)

RATE_LIMIT_LUA = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return count
"""

_redis_url = ""
_enabled = False
_fail_open = False
_key_prefix = "cardlearn:rate-limit"
_redis_client = None


def configure_rate_limit(
    redis_url: str,
    enabled: bool,
    fail_open: bool,
    key_prefix: str = "cardlearn:rate-limit",
):
    global _redis_url, _enabled, _fail_open, _key_prefix, _redis_client
    _redis_url = redis_url.strip()
    _enabled = enabled and bool(_redis_url)
    _fail_open = fail_open
    _key_prefix = key_prefix.strip() or "cardlearn:rate-limit"
    _redis_client = None


def is_rate_limit_enabled():
    return _enabled


def get_rate_limit_client():
    global _redis_client
    if not _enabled:
        return None
    if Redis is None:
        raise RateLimitBackendUnavailable("redis package is not installed")
    if _redis_client is None:
        _redis_client = Redis.from_url(
            _redis_url,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
    return _redis_client


def set_rate_limit_client(redis_client):
    global _redis_client
    _redis_client = redis_client


def hashed_rate_limit_key(identifier: str):
    return hashlib.sha256(identifier.encode("utf-8")).hexdigest()


def rate_limit_headers(result: RateLimitResult):
    return {
        "Retry-After": str(result.retry_after),
        "X-RateLimit-Limit": str(result.rule.limit),
        "X-RateLimit-Remaining": str(result.remaining),
        "X-RateLimit-Reset": str(result.reset_at),
        "X-RateLimit-Policy": f"{result.rule.limit};w={result.rule.window_seconds}",
    }


def record_rate_limit_hit(rule: RateLimitRule, identifier: str):
    try:
        redis_client = get_rate_limit_client()
        if redis_client is None:
            return None

        now_ts = int(time.time())
        window_id = now_ts // rule.window_seconds
        reset_at = (window_id + 1) * rule.window_seconds
        retry_after = max(reset_at - now_ts, 1)
        redis_key = f"{_key_prefix}:{rule.name}:{hashed_rate_limit_key(identifier)}:{window_id}"

        count = int(redis_client.eval(RATE_LIMIT_LUA, 1, redis_key, rule.window_seconds + 5))
        return RateLimitResult(
            rule=rule,
            count=count,
            retry_after=retry_after,
            reset_at=reset_at,
        )
    except Exception as error:
        if _fail_open:
            print(f"[RATE LIMIT] fail-open rule={rule.name} error={error}")
            return None
        raise RateLimitBackendUnavailable(str(error)) from error


def enforce_rate_limit(rule: RateLimitRule, identifier: str):
    result = record_rate_limit_hit(rule, identifier)
    if result is not None and not result.allowed:
        raise RateLimitExceeded(result)
