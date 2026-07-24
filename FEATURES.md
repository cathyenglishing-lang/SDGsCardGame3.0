# SDGsprogram_5.0 現有功能說明

更動日：20260613  
版本：5.0.0  
系統名稱：CardLearn SDGs / SDGsprogram_5.0

## 一、系統概述

SDGsprogram_5.0 是一套結合 SDGs 永續發展目標、英語口說任務與卡牌互動遊戲的學習平台。系統以 FastAPI 作為後端 API，靜態 HTML/CSS/JavaScript 作為前端頁面，提供學生註冊、登入、選擇 SDG 主題、進行 Pecha Kucha 卡牌配對遊戲、查看結果，以及教師端題庫與學習紀錄管理。

## 二、學生端功能

### 1. 首頁導覽

- 提供 CardLearn SDGs 平台介紹。
- 以互動式桌面、SDGs 說明、Pecha Kucha 任務介紹與 3D 地球視覺區塊呈現學習情境。
- 可導向註冊、登入與遊戲入口頁。

### 2. 會員註冊

- 支援姓名、性別、生日、Email、密碼與隱私同意欄位。
- 使用 Email OTP 驗證流程。
- 密碼需符合基本強度規則。
- 註冊成功後可使用帳號登入平台。

### 3. 登入與登入狀態保存

- 使用 Email 與密碼登入。
- 登入成功後由後端簽發 JWT。
- 前端將登入資訊保存於 localStorage，供後續頁面與 API 使用。
- 支援登出與登入檢查。

### 4. 遊戲入口

- 學生可選擇 SDG 主題與 CEFR 難度。
- 目前預設支援 SDG 4、SDG 13、SDG 5，且可由教師後台擴充。
- 選擇結果會保存於瀏覽器，供 loading、game、finish 頁面共用。

### 5. Loading 任務準備頁

- 顯示 SDGs 任務情境與 Pecha Kucha 簡介。
- 提供遊戲步驟說明。
- 可從準備頁進入正式卡牌遊戲。

### 6. SDG Pecha Kucha Card Game

- 依 SDG、難度與 Part 載入題庫。
- 遊戲結構為 SDG -> Part -> Subtopic -> sentence cards。
- 支援抽卡、聽句子、配對題目與完成 Part。
- 記錄錯誤次數、重聽次數與作答時間。
- 完成所有 Part 後結束遊戲並產生學習結果。

### 7. 結果頁

- 顯示單次遊戲 session 結果。
- 呈現各 Part 的錯誤次數、重聽次數與花費時間。
- 顯示同 SDG 與同難度下的平均表現，協助學生對照自己的學習狀況。

## 三、教師與管理端功能

### 1. 教師權限控管

- 使用者角色包含 student、teacher、admin。
- 教師後台僅 teacher 與 admin 可進入。
- 學生不可存取教師管理 API。

### 2. SDGs Card Game 題庫管理

- 新增或更新 SDG 主題。
- 新增或更新難度選項。
- 新增或更新 Part。
- 新增或更新 Subtopic。
- 依 Subtopic 與難度新增或更新 sentence card。
- 支援刪除 SDG、Part、Subtopic 與 Card。
- 刪除 SDG 或 Part 時會連動刪除下層內容。

### 3. 學習紀錄管理

- 查看學生遊戲 session。
- 查看每次遊戲的 SDG、難度、完成狀態、時間與表現。
- 查看各 Part 的平均錯誤、平均重聽與平均花費時間。
- 支援刪除指定遊戲紀錄。

### 4. 使用者管理

- 查看註冊帳號清單。
- 統計 student、teacher、admin 數量。
- 調整使用者角色。
- 刪除使用者，並連動刪除該使用者的遊戲紀錄與 OTP 紀錄。
- admin 帳號不可被刪除。

## 四、後端 API 功能

### 1. Auth API

- `POST /auth/send-otp`：寄送 Email OTP。
- `POST /auth/verify-otp`：驗證 OTP。
- `POST /auth/register`：註冊新使用者。
- `POST /auth/login`：登入並取得 JWT。
- `GET /auth/me`：取得目前登入者資訊。

### 2. Content API

- `GET /content/options`：取得可用 SDG 與難度選項。
- `GET /content/parts`：取得 SDG 題庫結構與卡牌資料。

### 3. Game API

- `GET /game/content`：取得指定 SDG 與難度的遊戲內容。
- `POST /game/start`：建立遊戲 session。
- `POST /game/part`：儲存 Part 作答紀錄。
- `POST /game/end`：結束遊戲 session。
- `GET /game/results/{session_id}`：取得遊戲結果。

### 4. Teacher API

- `GET /teacher/content`：取得教師後台題庫資料。
- `GET /teacher/game-records`：取得遊戲紀錄與統計。
- `DELETE /teacher/game-records/{session_id}`：刪除遊戲紀錄。
- `GET /teacher/users`：取得使用者清單與統計。
- `PATCH /teacher/users/{user_id}/role`：調整使用者角色。
- `DELETE /teacher/users/{user_id}`：刪除使用者。
- `POST /teacher/sdgs`：新增或更新 SDG。
- `POST /teacher/difficulties`：新增或更新難度。
- `POST /teacher/parts`：新增或更新 Part。
- `POST /teacher/sub-topics`：新增或更新 Subtopic。
- `POST /teacher/cards`：新增或更新 Card。
- `DELETE /teacher/sdgs/{sdg_level}`：刪除 SDG。
- `DELETE /teacher/parts/{part_id}`：刪除 Part。
- `DELETE /teacher/sub-topics/{sub_topic_id}`：刪除 Subtopic。
- `DELETE /teacher/cards/{card_id}`：刪除 Card。

## 五、資料儲存與資料表

- 本機預設使用 SQLite：`sql/app.db`。
- 部署時可透過 `DATABASE_URL` 改用 PostgreSQL。
- 主要資料表包含：
  - `users`：使用者資料與角色。
  - `email_otps`：Email OTP 驗證資料。
  - `sdg_options`：SDG 主題。
  - `difficulty_options`：難度選項。
  - `tbl_sdg_parts`：SDG Part。
  - `tbl_sdg_sub_topics`：Part 下的 Subtopic。
  - `tbl_sdg_cards`：依 Subtopic 與難度設定的卡牌句子。
  - `game_sessions`：遊戲 session。
  - `game_part_records`：各 Part 作答紀錄。

## 六、安全與部署支援

- JWT 登入驗證。
- 密碼雜湊儲存。
- Email OTP 驗證。
- CORS 可透過環境變數設定。
- Redis rate limiting 可透過 `REDIS_URL` 啟用。
- 支援本機 SQLite、Railway PostgreSQL、Vercel 靜態前端部署。
- 初始管理員可透過 `INITIAL_ADMIN_NAME`、`INITIAL_ADMIN_EMAIL`、`INITIAL_ADMIN_PASSWORD` 建立。

## 七、版本 5.0.0 重點

- 整合 SDGs 主題選擇、卡牌遊戲、學習紀錄與教師後台。
- 補齊教師端內容管理、遊戲紀錄統計與使用者角色管理。
- 加入 Email OTP、JWT、Redis rate limiting 與 PostgreSQL 部署支援。
- 補充專案 README、現有功能文件與更新紀錄。
