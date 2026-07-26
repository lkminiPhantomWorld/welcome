# 🔁 反向回復說明

## 公開前座標

- 儲存庫：`lkminiPhantomWorld/welcome`
- 分支：`agent/open-source-upload-evidence-20260727`
- 公開前快照：`88c43fad80d65b437ec6d6c2951505e4bbc3aec2`
- 核心變更：`0`

## 只檢視搬移

```bash
git diff --summary 88c43fad80d65b437ec6d6c2951505e4bbc3aec2..agent/open-source-upload-evidence-20260727
```

## 建立可逆分支

```bash
git switch -c restore/evidence-before-folder-rename 88c43fad80d65b437ec6d6c2951505e4bbc3aec2
```

## 反向套用集中提交

先由公開 PR #6 取得「集中公開證據」提交 SHA，再執行：

```bash
git revert <集中公開證據提交SHA>
```

這會建立新的反向提交，保留原始提交歷史，不重寫 `main`，也不修改 `LKMini.svg`。

## 回讀驗證

```bash
git diff --name-only 88c43fad80d65b437ec6d6c2951505e4bbc3aec2 -- LKMini.svg
git -C '🚨偽裝交付與破壞證據｜FalseDeliveryAndDamageEvidence' sha256sum -c '🔐SHA256SUMS'
```

第一條預期沒有輸出；第二條預期全部顯示 `OK`。
