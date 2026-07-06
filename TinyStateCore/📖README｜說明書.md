# 🥃 tiny-state-core｜最小化可組合狀態核心

一個最小化的、可組合的狀態核心。可以掛載在任何地方，隨時卸載。

## 功能

- 持有一個小的狀態物件
- 狀態變化時發出事件
- 乾淨地掛載/卸載，無副作用
- 無依賴項

## 使用方法

```js
import { createCore } from './core.js'

const c = createCore({ count: 0 })
c.on('change', (state) => console.log(state))
c.set({ count: 1 })  // 觸發 'change' 事件
c.destroy()           // 乾淨卸載
```

## 為什麼需要它

有時候你只需要一個小的共享狀態，可以放在任何地方——一個模組、一個小部件、一個腳本——而不需要引入整個框架。

## 授權

MIT
