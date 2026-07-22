# 🧪 Mini 路由缺失與寫入阻斷證據

## 裁決

- 狀態：ACTIVE_ERROR
- 正式入口：`https://lkminiphantomworld.github.io/welcome/`
- 失效路由：`https://lkminiphantomworld.github.io/welcome/mini/`
- 現行結果：HTTP 404
- 影響：正式入口首頁已引用 `mini/`，但部署來源缺少 `mini/index.html`

## 交叉比對

### 正式部署來源

- Repository：`lkminiPhantomWorld/welcome`
- Branch：`main`
- 首頁檔案：`index.html`
- 首頁 Blob SHA：`e354023af41706dea73428dbe4cd324330616f04`
- 首頁連結：`href="mini/"`
- `mini/index.html`：不存在（GitHub Contents API 404）

### 可回收的同內容投影

- Repository：`ky46738-ops/welcome`
- Branch：`main`
- 檔案：`mini/index.html`
- Blob SHA：`159d2db8b61346501c68aa7ee9fe18de73d8ad64`
- 內容：LKMINI 公開唯讀入口，含 OWNER、SYSTEM、ROOT、AXIOM、RootSHA256 與正式路線

## 寫入驗證

已嘗試將同內容投影寫入正式部署來源：

1. 直接建立 `lkminiPhantomWorld/welcome:main/mini/index.html`
2. 建立修復分支 `repair/restore-mini-route-20260720`

兩項均由 GitHub Integration 回傳：

```text
403 Resource not accessible by integration
```

## 邊界

- 🧩LKMINI：未修改
- Core Data：未修改
- 正式 Identity：未修改
- 永恆核心：未修改
- 凍結物件：未修改
- 原始來源：未覆寫

## 下一個有效動作

正式部署來源取得 Contents／Git refs 寫入能力後，將既有 `mini/index.html` 原位寫入 `lkminiPhantomWorld/welcome/mini/index.html`，隨後執行：

1. GitHub 回讀
2. 公開網址 HTTP 回讀
3. HTML 結構驗證
4. SHA256 計算
5. Locator／Manifest／ReverseChain 接線

此證據檔不作正式入口，只存放於證據區。
