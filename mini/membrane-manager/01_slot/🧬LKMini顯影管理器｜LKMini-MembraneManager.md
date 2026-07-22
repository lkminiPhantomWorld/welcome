# 🧬 LK Mini 顯影管理器 v2.0 | 88層膜總表

🥃 收到。骨頭已升級。開始給88個世界穿膜。

規則：不變。。

***

## 🖼 無損圖像世界 | Glass & Transparent Membrane

| 副檔名 | 膜類型 | 透光率 | properties | 風險Lv |
|---|---|---|---|---|
| `.png` | Transparent_Membrane | `5%` | ["Lossless", "Alpha_Channel"] | Lv.1 |
| `.webp` | Transparent_Membrane | `5%` | ["Lossless", "Alpha_Channel"] | Lv.1 |
| `.svg` | Glass_Membrane | `0%` | ["Vector", "Infinite_Scale"] | Lv.1 |
| `.bmp` | Glass_Membrane | `0%` | ["Raw", "No_Compression"] | Lv.1 |
| `.tiff` | Transparent_Membrane | `5%` | ["Lossless", "Layers"] | Lv.1 |

## 🗜 有損圖像世界 | Frosted Membrane

| 副檔名 | 膜類型 | 透光率 | properties | 風險Lv |
|---|---|---|---|---|
| `.jpg .jpeg` | Frosted_Membrane | `40%` | ["DCT_Lossy", "No_Alpha"] | Lv.2 |
| `.avif` | Frosted_Membrane | `30%` | ["Modern_Lossy", "Alpha"] | Lv.2 |
| `.heic` | Frosted_Membrane | `35%` | ["Apple_Lossy", "Alpha"] | Lv.2 |

## 🎞 視頻音頻世界 | Frosted/Armor Membrane

| 副檔名 | 膜類型 | 透光率 | properties | 風險Lv |
|---|---|---|---|---|
| `.mp4 .mkv` | Frosted_Membrane | `45%` | ["H264", "Temporal_Lossy"] | Lv.2 |
| `.wav` | Glass_Membrane | `0%` | ["PCM_Raw"] | Lv.1 |
| `.mp3` | Frosted_Membrane | `50%` | ["Psychoacoustic_Lossy"] | Lv.2 |

## 💻 程式腳本世界 | Execution Membrane

| 副檔名 | 膜類型 | 透光率 | properties | 風險Lv |
|---|---|---|---|---|
| `.py .js` | Execution_Membrane | `0%` | ["Source_Code", "Readable"] | Lv.3 |
| `.exe .dll` | Armor_Membrane | `90%` | ["Binary", "Compiled"] | Lv.4 |
| `.wasm` | Armor_Membrane | `85%` | ["Sandboxed_Binary"] | Lv.3 |

## 📦 容器壓縮世界 | Armor Membrane

| 副檔名 | 膜類型 | 透光率 | properties | 風險Lv |
|---|---|---|---|---|
| `.zip .7z` | Armor_Membrane | `80%` | ["Archive", "Need_Extract"] | Lv.2 |
| `.tar` | Armor_Membrane | `75%` | ["Stream_Archive"] | Lv.2 |

## 🔒 加密安全世界 | Blackout Membrane

| 副檔名 | 膜類型 | 透光率 | properties | 風險Lv |
|---|---|---|---|---|
| `.aes .gpg` | Blackout_Membrane | `100%` | ["Encrypted", "No_Key_No_Body"] | Lv.5 |
| `.sha256` | Glass_Membrane | `0%` | ["Fingerprint_Only"] | Lv.1 |

## 📝 文本數據世界 | Glass Membrane

| 副檔名 | 膜類型 | 透光率 | properties | 風險Lv |
|---|---|---|---|---|
| `.txt .md` | Glass_Membrane | `0%` | ["Plain_Text"] | Lv.1 |
| `.json .xml` | Glass_Membrane | `0%` | ["Structured_Text"] | Lv.1 |
| `.csv` | Glass_Membrane | `0%` | ["Table_Text"] | Lv.1 |

## 🔬 專業格式 | Mixed Membrane

| 副檔名 | 膜類型 | 透光率 | properties | 風險Lv |
|---|---|---|---|---|
| `.pdf` | Frosted_Membrane | `20%` | ["Vector+Raster", "Locked"] | Lv.2 |
| `.psd .ai` | Transparent_Membrane | `10%` | ["Layers", "Proprietary"] | Lv.2 |
| `.emerge` | Glass_Membrane | `0%` | ["LK_Mini_Bone", "Self_Describing"] | Lv.0 |

***

## 程式碼補丁

```python
MEMBRANE_REGISTRY = {
  ".png":  {"type": "Transparent_Membrane", "opacity": 0.05, "lv": 1},
  ".jpg":  {"type": "Frosted_Membrane",     "opacity": 0.40, "lv": 2},
  ".aes":  {"type": "Blackout_Membrane",    "opacity": 1.00, "lv": 5},
  ".txt":  {"type": "Glass_Membrane",       "opacity": 0.00, "lv": 1},
  ".emerge": {"type": "Glass_Membrane",     "opacity": 0.00, "lv": 0},
}

def project(bone_sha256: str, target_ext: str) -> bytes:
    membrane = MEMBRANE_REGISTRY[target_ext]
    if membrane["opacity"] == 1.0:
        raise PermissionError("Blackout_Membrane: 沒鑰匙，投影失敗")
    return render(bone_sha256, membrane)
```

***

🥃 骨架施工完成。
