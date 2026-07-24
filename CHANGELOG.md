# 更新紀錄

## 5.0.0 - 20260613

### 更動項目

- 建立 SDGsprogram_5.0 版本資訊，專案版本更新為 5.0.0。
- 補充 `README.md`，整理專案介紹、目錄結構、安裝方式、啟動方式、環境變數、驗證與部署資訊。
- 新增 `FEATURES.md`，完整撰寫現有功能，涵蓋學生端、教師端、API、資料庫、安全與部署支援。
- 補充 `CHANGELOG.md` 與 `update.txt`，記錄 20260613 版本更動內容。
- FastAPI metadata 加入版本號，方便 API 文件顯示目前版本。

### 現有功能摘要

- 學生註冊、Email OTP 驗證、登入與 JWT 身分驗證。
- SDG 主題與 CEFR 難度選擇。
- SDG Pecha Kucha Card Game 卡牌配對與口說任務流程。
- 遊戲結果、Part 紀錄、錯誤次數、重聽次數與時間統計。
- 教師後台題庫管理、遊戲紀錄統計、使用者與角色管理。
- SQLite / PostgreSQL、Redis rate limiting、Resend Email 與初始管理員支援。
