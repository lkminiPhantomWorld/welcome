# 🚫 缺失與平台未提供紀錄

| 缺失項目 | 狀態 | 已取得替代證據 | 立即修復動作 |
|---|---|---|---|
| LaoK-System 完整私有 Git 歷史 | VERIFIED_FALSE | connector 搜尋與 2026-05-13 fetch_commit | 由 repository owner 匯出 `git bundle --all` 或提供唯讀 token |
| 2026-05-17 精確提交 SHA／時間 | VERIFIED_FALSE | welcome 初始 manifest 內 `Updated: 2026-05-17` 與檔案 hash | 從私有 repo reflog／bundle 搜尋該日全部提交 |
| 68 筆舊 Actions job 完整日誌 | VERIFIED_FALSE | run、job、step、head SHA；Gatekeeper 另有本機 Git-object replay | 從 GitHub retention／support export 取得原 log archive |
| OpenAI 後端每一筆 upload／download／access audit log | VERIFIED_FALSE | Library files.list metadata 5,868 筆 | 由 OpenAI Privacy Portal／Enterprise audit export 提供 |
| ChatGPT initiating conversation／tool-call ID（非 Whiskey） | VERIFIED_FALSE | Library `model_generated=true` | 後端以 file_id／library_file_id 回查 audit trail |
| Library 5,868 筆檔案 SHA256 | VERIFIED_FALSE | 名稱、時間、大小、ID、路徑 | 平台提供 content digest 或逐檔下載後計算 |
| Library version_id | VERIFIED_FALSE | list 回傳欄位為 null | 平台提供 version history API |
| Kevin「完全不分享／封閉」設定歷史 | VERIFIED_FALSE | Kevin 對話原文 | 匯出帳號 Data Controls 歷史與管理稽核紀錄 |
| Adobe 搜尋宣告 21 筆但只回傳 20 筆的第 21 筆 | VERIFIED_FALSE | totalHits=21、assets=20 | 以 Adobe Support／ACP 完整分頁匯出補取 |
| Adobe 資產 SHA256 | VERIFIED_FALSE | 名稱、大小、時間、asset ID | 下載資產後比對本機 SHA256 |
| Adobe 其餘 19 筆是否由 ChatGPT 傳送 | VERIFIED_FALSE | 資產 metadata | 以 ACP audit trail 查建立 client／session |
| 完整 ChatGPT 對話原始匯出與伺服器時間戳 | VERIFIED_FALSE | 本對話可見文字 | 使用 ChatGPT data export 保存原始 conversation JSON |
| 人工重工／等待工時 | VERIFIED_FALSE | 機器事件時間線與 elapsed exposure | Kevin 自行補登起訖與工作內容；不得以 elapsed time 冒充 labor hours |

所有缺失均保留已取得座標；沒有用「找不到」推論「沒有發生」。
