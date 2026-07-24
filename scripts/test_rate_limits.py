"""
Self-test tool for the Redis rate limiter.

This script verifies the configured rate-limit rules without requiring a real
Redis server and without calling external email providers.
"""

from __future__ import annotations

import argparse
import sys
import time as real_time
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class FakeClock:
    def __init__(self, start: int = 1_800_000_000):
        self.current = start

    def time(self):
        return self.current

    def advance(self, seconds: int):
        self.current += seconds


class MemoryRedis:
    def __init__(self, clock: FakeClock, fail: bool = False):
        self.clock = clock
        self.fail = fail
        self.values: dict[str, int] = {}
        self.expires_at: dict[str, int] = {}

    def eval(self, script, numkeys, key, ttl):
        if self.fail:
            raise ConnectionError("simulated redis outage")
        self._expire_old_keys()
        self.values[key] = self.values.get(key, 0) + 1
        if self.values[key] == 1:
            self.expires_at[key] = int(self.clock.time()) + int(ttl)
        return self.values[key]

    def _expire_old_keys(self):
        now = int(self.clock.time())
        expired_keys = [key for key, expires_at in self.expires_at.items() if expires_at <= now]
        for key in expired_keys:
            self.values.pop(key, None)
            self.expires_at.pop(key, None)


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str


def import_rate_limit_module():
    try:
        from backend import rate_limit
    except Exception as error:
        raise SystemExit(
            "Cannot import backend.rate_limit.\n\n"
            f"Original error: {error}"
        ) from error
    return rate_limit


def install_fake_redis(rate_limit, clock: FakeClock, fail: bool = False):
    rate_limit.configure_rate_limit(
        redis_url="redis://rate-limit-self-test",
        enabled=True,
        fail_open=False,
        key_prefix="cardlearn:test-rate-limit",
    )
    rate_limit.Redis = object
    rate_limit.set_rate_limit_client(MemoryRedis(clock, fail=fail))
    rate_limit.time.time = clock.time


def reset_fake_redis(rate_limit, clock: FakeClock):
    rate_limit.set_rate_limit_client(MemoryRedis(clock))


def check_rule(rate_limit, clock: FakeClock, rule, identifier: str):
    reset_fake_redis(rate_limit, clock)

    for index in range(rule.limit):
        try:
            rate_limit.enforce_rate_limit(rule, identifier)
        except Exception as error:
            raise AssertionError(f"request {index + 1} should pass, got {error}") from error

    try:
        rate_limit.enforce_rate_limit(rule, identifier)
    except rate_limit.RateLimitExceeded as error:
        headers = rate_limit.rate_limit_headers(error.result)
        if headers.get("X-RateLimit-Limit") != str(rule.limit):
            raise AssertionError("missing or incorrect X-RateLimit-Limit header")
        if headers.get("X-RateLimit-Remaining") != "0":
            raise AssertionError("missing or incorrect X-RateLimit-Remaining header")
        if "Retry-After" not in headers:
            raise AssertionError("missing Retry-After header")
    except Exception as error:
        raise AssertionError(f"expected RateLimitExceeded, got {error}") from error
    else:
        raise AssertionError("request above the limit should be blocked")

    clock.advance(rule.window_seconds + 1)
    try:
        rate_limit.enforce_rate_limit(rule, identifier)
    except Exception as error:
        raise AssertionError("first request in a new window should pass") from error


def run_checks(rate_limit):
    original_time = rate_limit.time.time
    clock = FakeClock()
    install_fake_redis(rate_limit, clock)

    checks = [
        (
            "global API: 60 requests per IP per minute",
            rate_limit.GLOBAL_API_RATE_LIMIT,
            "ip:203.0.113.10",
        ),
        (
            "login: 10 requests per IP per 5 minutes",
            rate_limit.LOGIN_RATE_LIMIT,
            "ip:203.0.113.20",
        ),
        (
            "register: 5 requests per IP per 10 minutes",
            rate_limit.REGISTER_RATE_LIMIT,
            "ip:203.0.113.30",
        ),
        (
            "send OTP: 3 requests per email per 5 minutes",
            rate_limit.SEND_OTP_RATE_LIMIT,
            "email:student@example.com",
        ),
        (
            "save game record: 20 requests per user per minute",
            rate_limit.GAME_RECORD_RATE_LIMIT,
            "user:42",
        ),
    ]

    results: list[CheckResult] = []
    try:
        for name, rule, identifier in checks:
            try:
                check_rule(rate_limit, clock, rule, identifier)
                results.append(CheckResult(name, True, "passed"))
            except Exception as error:
                results.append(CheckResult(name, False, str(error)))

        reset_fake_redis(rate_limit, clock)
        email_identifier = "email:privacy-check@example.com"
        rate_limit.enforce_rate_limit(rate_limit.SEND_OTP_RATE_LIMIT, email_identifier)
        redis_keys = list(rate_limit._redis_client.values.keys())
        key_text = "\n".join(redis_keys)
        if "privacy-check@example.com" in key_text:
            results.append(CheckResult("Redis key does not expose raw email", False, "raw email found in Redis key"))
        else:
            results.append(CheckResult("Redis key does not expose raw email", True, "passed"))

        install_fake_redis(rate_limit, clock, fail=True)
        try:
            rate_limit.enforce_rate_limit(rate_limit.LOGIN_RATE_LIMIT, "ip:203.0.113.40")
        except rate_limit.RateLimitBackendUnavailable:
            results.append(CheckResult("Redis outage defaults to fail-closed", True, "passed"))
        except Exception as error:
            results.append(CheckResult("Redis outage defaults to fail-closed", False, str(error)))
        else:
            results.append(CheckResult("Redis outage defaults to fail-closed", False, "request was allowed"))
    finally:
        rate_limit.time.time = original_time

    return results


def main():
    parser = argparse.ArgumentParser(description="Run automated checks for Redis rate limits.")
    parser.add_argument("--quiet", action="store_true", help="Only print failures and final summary.")
    args = parser.parse_args()

    start_time = real_time.time()
    rate_limit = import_rate_limit_module()
    results = run_checks(rate_limit)
    failed = [result for result in results if not result.passed]

    for result in results:
        if args.quiet and result.passed:
            continue
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.name} - {result.detail}")

    elapsed = real_time.time() - start_time
    print(f"\nSummary: {len(results) - len(failed)}/{len(results)} checks passed in {elapsed:.2f}s")

    if failed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
