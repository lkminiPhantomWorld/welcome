// 基本煙霧測試 — 執行命令: node test.js
const { createCore } = require('./core.js');

let passed = 0;
let failed = 0;

function assert(label, expr) {
  if (expr) { console.log('  ✓', label); passed++; }
  else       { console.error('  ✗', label); failed++; }
}

// 1. 初始狀態
const c = createCore({ x: 1 });
assert('get() 返回初始狀態', c.get().x === 1);

// 2. 設置 + 變化事件
let received = null;
const off = c.on('change', s => { received = s; });
c.set({ x: 2 });
assert('set() 更新狀態', c.get().x === 2);
assert('change 事件觸發', received && received.x === 2);

// 3. 取消訂閱
off();
c.set({ x: 3 });
assert('off() 停止監聽', received.x === 2); // 應該仍是 2

// 4. 重置
const c2 = createCore({ y: 10 });
c2.set({ y: 99 });
c2.reset();
assert('reset() 恢復初始狀態', c2.get().y === 10);

// 5. 銷毀
c2.destroy();
try { c2.get(); assert('銷毀後 get 拋出錯誤', false); }
catch (e) { assert('銷毀後 get 拋出錯誤', true); }

console.log(`\n${passed} 通過, ${failed} 失敗`);
if (failed > 0) process.exit(1);
