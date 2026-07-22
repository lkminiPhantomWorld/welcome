# tiny-state-core

一個極簡、可組合的狀態核心。可掛載在任何地方，也可隨時卸載。

## 它做什麼

- 保存一個小型狀態物件
- 狀態變更時發出事件
- 可乾淨掛載 / 卸載，不產生副作用
- 無相依套件

## 用法

```js
import { createCore } from './core.js'

const c = createCore({ count: 0 })
c.on('change', (state) => console.log(state))
c.set({ count: 1 })  // 觸發 'change'
c.destroy()           // 乾淨卸載
```

## 為什麼

有時你只需要一小塊可共享的狀態，它可以存在於任何地方——模組、小工具、腳本——而不用引入整個框架。

## 授權

MIT
