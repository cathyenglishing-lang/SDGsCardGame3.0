# Redis 流量控制開發文件

日期：2026-05-23

## 需求

本次開發目標是在 FastAPI 後端加入 Redis-based rate limiting，限制如下：

| 功能 | 限制 |
| --- | ---: |
| 全站 API | 每 IP 每分鐘 60 次 |
| 登入 | 每 IP 每 5 分鐘 10 次 |
| 註冊 | 每 IP 每 10 分鐘 5 次 |
| 寄驗證信 | 每 email 每 5 分鐘 3 次 |
| 儲存遊戲紀錄 | 每 user 每分鐘 20 次 |

## 放置位置

開發紀錄放在 `dev/redis-rate-limit.md`。專案原本已有 `DEPLOYMENT.md`，但沒有專門紀錄功能開發脈絡的資料夾，因此新增 `dev/` 作為後續功能設計、實作決策與驗證方式的集中位置。

## 實作摘要

主要修改檔案：

- `backend/rate_limit.py`
- `backend/main.py`
- `scripts/test_rate_limits.py`
- `requirements.txt`
- `backend/requirements.txt`
- `.env.example`
- `DEPLOYMENT.md`

後端新增固定視窗計數器。每次命中受控路徑時，依限制規則產生 Redis key，使用 Redis Lua script 原子化執行 `INCR` 與首次 TTL 設定，讓視窗到期後自動釋放。

Redis key 使用 SHA-256 雜湊識別值，避免 email、IP、user id 直接暴露在 Redis key 中。key 格式如下：

```text
{RATE_LIMIT_KEY_PREFIX}:{rule_name}:{hashed_identifier}:{window_id}
```

## 規則對應

- 全站 API：middleware 套用於 `/auth`、`/content`、`/game`、`/teacher`、`/health`，不計算前端頁面與靜態資源。
- 登入：`POST /auth/login`，識別值為 client IP。
- 註冊：`POST /auth/register`，識別值為 client IP。
- 寄驗證信：`POST /auth/send-otp`，識別值為 normalize 後的 email。
- 儲存遊戲紀錄：`POST /game/part`，通過 JWT 後以目前 user id 作為識別值。

超量時回傳：

```http
429 Too Many Requests
Retry-After: <seconds>
X-RateLimit-Limit: <limit>
X-RateLimit-Remaining: 0
X-RateLimit-Reset: <unix timestamp>
```

如果設定了 Redis 但 Redis 不可用，預設回傳 `503 Rate limit service unavailable.`，避免在保護機制失效時繼續放行大量請求。

## 環境變數

```env
REDIS_URL=
RATE_LIMIT_ENABLED=true
RATE_LIMIT_FAIL_OPEN=false
RATE_LIMIT_KEY_PREFIX=cardlearn:rate-limit
```

說明：

- `REDIS_URL`：Redis 連線字串。未設定時，本機開發會停用流量控制。
- `RATE_LIMIT_ENABLED`：可在需要時暫停 rate limiter。
- `RATE_LIMIT_FAIL_OPEN`：`false` 時 Redis 異常會回 `503`；`true` 時會先放行請求並輸出 log。
- `RATE_LIMIT_KEY_PREFIX`：Redis key 前綴，可用於區分環境。

## 部署注意事項

Railway 後端需新增 Redis service，並把 Redis 提供的連線字串設定為 `REDIS_URL`。正式環境建議保留：

```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_FAIL_OPEN=false
```

若使用反向代理或 Railway，IP 來源會優先讀取 `X-Forwarded-For` 第一個 IP，其次為 `X-Real-IP`，最後才使用 FastAPI request client host。

## 驗證方式

語法檢查：

```bash
python -m py_compile backend/main.py
```

自動測試工具：

```bash
python scripts/test_rate_limits.py
```

此工具會直接載入 `backend.main`，注入記憶體版 Redis，測試五條限制規則是否會在超量時回傳 `429`，並確認視窗過期後可重新放行。它也會檢查 Redis key 不包含原始 email，以及 Redis 異常時預設回傳 `503`。測試過程不需要啟動真實 Redis，也不會呼叫寄信 API。

本機若未啟動 Redis，`REDIS_URL` 留空即可確認原 API 可正常啟動。要驗證限制效果，可啟動 Redis 後設定：

```env
REDIS_URL=redis://localhost:6379/0
```

接著重複呼叫受控端點，例如 `/health` 超過 60 次，或對同一 email 呼叫 `/auth/send-otp` 超過 3 次，預期會得到 `429` 與 `Retry-After` header。

## 後續可擴充

- 若需要更平滑的限制，可改為 sliding window 或 token bucket。
- 若要對不同角色套用不同配額，可在通過 JWT 後依 role 選擇規則。
- 若要讓前端顯示等待時間，可讀取 `Retry-After` header 顯示倒數。
