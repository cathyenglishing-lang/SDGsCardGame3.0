# SDGsprogram_5.0

更動日：20260613  
版本：5.0.0  
系統名稱：CardLearn SDGs

SDGsprogram_5.0 是一套結合 SDGs 永續議題、英語口說與卡牌互動任務的學習平台。學生可以註冊登入、選擇 SDG 主題與難度、進行 Pecha Kucha 卡牌配對遊戲並查看結果；教師與管理者可以維護題庫、查看學習紀錄、管理使用者角色。

## 專案結構

```text
backend/                 FastAPI 後端，主要程式為 backend/main.py
frontend/                靜態前端原始碼
frontend/pages/          登入、註冊、遊戲入口、遊戲、結果、教師後台頁面
frontend/js/api.js       前端 API 呼叫集中管理
dist/                    前端 build 後輸出，供 Vercel 靜態部署使用
scripts/                 build、測試與資料庫遷移腳本
sql/                     本機 SQLite 資料庫
dev/                     開發補充文件
```

## 主要功能

- 會員註冊、Email OTP 驗證、登入與 JWT 驗證。
- 學生端 SDG 主題與難度選擇。
- SDG Pecha Kucha Card Game 卡牌配對遊戲。
- 遊戲 session、Part 作答紀錄、錯誤次數、重聽次數與時間紀錄。
- 結果頁顯示個人表現與同題組平均表現。
- 教師後台維護 SDG、難度、Part、Subtopic 與 Card 題庫。
- 教師後台查看遊戲紀錄、統計與使用者資料。
- teacher/admin 權限控管。
- SQLite / PostgreSQL 雙資料庫支援。
- Redis rate limiting、CORS、Resend Email 與初始管理員設定。

更完整的現有功能請參考 [FEATURES.md](FEATURES.md)。

## 環境需求

- Python 3.12+
- Node.js 與 npm
- SQLite（本機預設）
- PostgreSQL（部署時選用）
- Redis（rate limiting 選用）

## 安裝

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

如需前端 build，請確認 Node.js / npm 可用。

## 環境變數

請以 `.env.example` 為範本建立 `.env`，不要提交真實密鑰。

常用設定：

```text
DATABASE_URL=
REDIS_URL=
RATE_LIMIT_ENABLED=true
RATE_LIMIT_FAIL_OPEN=false
SECRET_KEY=replace-with-a-long-random-secret
FRONTEND_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
API_BASE_URL=http://127.0.0.1:8000
RESEND_API_KEY=
RESEND_FROM=CardLearn SDGs <onboarding@resend.dev>
INITIAL_ADMIN_NAME=Admin
INITIAL_ADMIN_EMAIL=
INITIAL_ADMIN_PASSWORD=
```

未設定 `DATABASE_URL` 時，系統會使用 `sql/app.db`。設定 `DATABASE_URL` 後，後端會使用 PostgreSQL。

## 本機執行

啟動 API 與前端靜態檔服務：

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

開啟：

```text
http://127.0.0.1:8000
```

## 前端 Build

```bash
npm run build
```

build script 會將 `frontend/` 複製到 `dist/` 與 `dist/static/`，並依 `API_BASE_URL` 或 `VITE_API_BASE_URL` 產生 config 檔。

## 驗證

Python syntax check：

```bash
python -m py_compile backend/main.py backend/rate_limit.py scripts/test_rate_limits.py
```

Redis rate-limit self-test：

```bash
python scripts/test_rate_limits.py
```

Frontend build check：

```bash
npm run build
```

## 部署

後端可部署至 Railway，並搭配 PostgreSQL 與 Redis。前端可透過 Vercel 使用 `dist/` 輸出進行靜態部署。詳細流程請參考 [DEPLOYMENT.md](DEPLOYMENT.md)。

## 更新紀錄

請參考 [CHANGELOG.md](CHANGELOG.md) 與 [update.txt](update.txt)。
