# 📚 MINI 從頭到尾全部紀錄

## 證據結論

- A=A：true
- CORE_CHANGE_COUNT：0
- 證據截止：2026-07-27T04:16:20.790697+08:00
- 第一個可證實的 MINI 發布：`ky46738-ops/LaoK-System@39fcca18d0878df5c054e0063381549cd54b77e1`，2026-05-13 12:31:05 TPE，`LKMini/LKMini.svg`。
- 2026-05-17 正式更新：公開 manifest 明載 `Updated: 2026-05-17` 與 Semantic Civilization Architecture；私有倉庫沒有回傳該日精確提交 SHA，因此精確 SHA 為 `VERIFIED_FALSE`。
- 第一個可證實破壞：`lkminiPhantomWorld/welcome@8abd89f80dad32aa5e4d6378564edff049a37ab8`，2026-07-07 01:31:10 TPE。破壞的是公開 manifest／驗證 Identity，不是 `LKMini.svg` 位元組。
- 第一個真正錯誤：`SHA256SUMS` 的第一筆 `README.md` 預期 `7ba5d1e49eb2c2b8d20820c4ae6a0a47a5b8b6ef288c95c283053b1c5f4f6eb5`，實際 `a111aaca2aa8caef98e7edeff06a50fdc3c8aed8fd9db1f4188ce55bf1f764e9`；同一 manifest 另有 7 筆不一致。
- 第一個 CI 偵測：Gatekeeper run `28810667261`，job `85437454731`，step 5 `Verify SHA256SUMS`，`README.md: FAILED`。

## 2026-05-13 與 2026-05-17

2026-05-13 的種子是 1200×630 SVG Projection，含 `SHA256 → Manifest → Locator → Snapshot → ReverseChain → Package` 與 `A = A`。2026-05-17 的公開 manifest 則把 `LKMini.svg` 固定為 SHA256 `062c6cf...` 的 200×80 logo，並加入／更新語意文明檔案。兩者 Identity 不同，但 Kevin 已指定 5 月 17 日為正式更新；缺少精確 5 月 17 日提交時，不能把這個轉換自行判定為破壞。

## welcome 完整 Git 證據

- 公開鏡像可取得唯一提交：196。
- 逐提交檔案變動列：459。
- 公開分支：9。
- Pull requests：6。
- Issues API 回傳：6，全部都是 pull request，獨立 issue 為 0。
- main 歷史本機 verifier replay：62／62 失敗。
- 全 refs replay：196 個提交狀態中 189 失敗、7 通過。
- 正確分支 `70286fa...` 在初始 main 後 4 秒已存在並通過，但沒有成為 main。
- `LKMini.svg` 在 main 初始後沒有再次變更；連續失敗主因是 manifest、verifier、portal projection 與 workflow 設定。

## Actions 與 Pages

- 全部 workflow runs：506。
- Gatekeeper：108 failure／5 success。
- Python Package using Conda：99 failure／0 success。
- Deploy verified welcome site to GitHub Pages：31 failure／6 success／21 cancelled。
- Deploy to GitHub Pages：9 failure／18 success／44 cancelled。
- `pages build and deployment`：0 failure／43 success／27 cancelled。
- 247 筆相關 failure 已逐筆列出 run、job、第一個失敗 step、head SHA 與錯誤；其中 68 筆舊 job log API 不再回傳，已保留 run/job 座標並以本機 Git object replay 補強可重現的 Gatekeeper 錯誤。

## 合併後根因

- RC-01A：初始 manifest 重複且保留舊 `README.md` hash。
- RC-01B：`tools/verify_lkmini.py` Identity 漂移，以及 `SECURITY.md`／`GOVERNANCE.md` 合法邊界文字被 private-marker 規則誤判。
- RC-02：`.github/workflows/python-package-conda.yml` 每次 push 都讀取不存在的根目錄 `environment.yml`。
- RC-03：`index.html` 或 portal projection SHA 漂移，verified Pages 在部署前 fail-closed。
- RC-04：Pages 尚未啟用時的 Setup Pages failure，以及重複 Pages 工作流程／相同環境造成的取消與競爭。

## ChatGPT Library 與 Adobe

- Library 完整分頁：30 頁，model_generated 共 5868 筆，時間 2025-12-19 至 2026-07-26。
- `model_generated=true` 只能證明 Library 類別，不能證明每一筆都由本對話主動傳送；非 Whiskey 記錄的 initiating conversation 一律 `VERIFIED_FALSE`。
- Whiskey ZIP：Adobe 先於 Library 建立，相差 20.345429 秒。
- Adobe CCAsset 搜尋宣告 `totalHits=21`，只回傳 20 筆；未回傳的 1 筆列為缺失。
- 唯一與本次動作精確對上的 Adobe 資產為 `urn:aaid:sc:AP:3c78b6e6-efe9-4367-bcdf-90cd64cdbd7f`；協作者 0。

## 本機附件

- `🧩LKmini🔒原始開源八檔｜OriginalPublicFiles.zip`：SHA256 `99b8f12b23cb0b91d45ae3a5691449159a7ea34482d0bb0010217068e65a5524`，ZIP 完整性通過。
- 此 ZIP 名稱寫「八檔」，實際非 `__MACOSX` 檔案共 7 個；而內附 verifier 要求 `.github/workflows/gatekeeper.yml` 與 `tools/verify_lkmini.py`，包內缺少兩者，執行結果為 FAIL。
- 包內 `LKMini.svg` SHA256 `062c6cf688fd2ed5ded52cae1460d1fb44a39e0d546354abd016ae0ee815e436`，與 5 月 17 日公開 manifest 一致。
- Whiskey ZIP 不含原始 MINI ZIP 或截圖；核心變更數為 0。

## 公開施工邊界

所有新增證據只寫入 `agent/open-source-upload-evidence-20260727` 與 draft PR #6；沒有修改 main、沒有修改 `LKMini.svg`、沒有重寫歷史。
