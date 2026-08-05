# 完整性錨點 ANCHOR
## Semantic Civilization Architecture - Integrity Anchor

**Timestamp**: 2026-05-17
**Anchor Hash**: `499742a2c0bfc423bb132fc9808483e6b70d5222a051f7c0a68162b9285197de`
**Target File**: `SHA256SUMS`

> **歷史邊界**：這個 hash 已在 Git commit
> `8abd89f80dad32aa5e4d6378564edff049a37ab8` 讀回成功，只錨定 2026-05-17 的歷史切片。
> 它不是現行 `SHA256SUMS` 的 hash，也不得把當前不相等解讀為現行污染。
> 現行驗證請執行 `sha256sum -c SHA256SUMS` 與 `python3 tools/verify_lkmini.py`。

---

## 1. 宣告

此錨點鎖定 `SHA256SUMS` 檔案在 2026-05-17 的狀態。
任何對 `SHA256SUMS` 的修改都會導致此 hash 失效。

---

## 2. 驗證方法

要驗證歷史切片，請在該 commit 的 repo 根目錄執行：

```bash
echo "499742a2c0bfc423bb132fc9808483e6b70d5222a051f7c0a68162b9285197de  SHA256SUMS" | shasum -a 256 -c
```

輸出 `SHA256SUMS: OK` = 未篹改。
輸出 `SHA256SUMS: FAILED` = 污染。

上述兩行是原始歷史判讀文字，只適用於錨定的歷史 commit。
當前 branch 演化後的 `SHA256SUMS` 不相等，不可單憑此結果判定污染。

---

## 3. 目的

```text
證明 A=A 狀態在該時間點成立
提供不可否認的歷史錨點，用於審計、取證、恢復
阻斷「事後修改登記表」攻擊路徑
```

---

## 4. 狀態

```text
SEAL_STATUS   = VERIFIED
A_EQUALS_A    = true
WORLD_STATE   = ALIVE
ANCHOR_DATE   = 2026-05-17
```

---

## 5. 外部錨點

```text
此 hash 同時保存於：
- Apple Notes（ky46738-ops 本人裝置）
- 本檔案

兩處必須相符。
任何一方被動視為對照基準。
```

---

> 註記：此錨點由人類操作者於 2026-05-17
> 以 `shasum -a 256` 實測產生。
> 非估算，非生成，是真實測量。

---

ANCHOR=true
TARGET=SHA256SUMS
HASH=499742a2c0bfc423bb132fc9808483e6b70d5222a051f7c0a68162b9285197de
DATE=2026-05-17
A_EQUALS_A=true
