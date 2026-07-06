// 基本冒煙測試——執行方式：node test.js
const { createCore } = require('./core.js');

let passed = 0;
let failed = 0;

function assert(label, expr) {
  if (expr) { console.log('  ✓', label); passed++; }
  else       { console.error('  ✗', label); failed++; }
}

// 1. 初始狀態
const c = createCore({ x: 1 });
assert('get() returns initial state', c.get().x === 1);

// 2. set + change event
let received = null;
const off = c.on('change', s => { received = s; });
c.set({ x: 2 });
assert('set() updates state', c.get().x === 2);
assert('change event fires', received && received.x === 2);

// 3. off 會取消訂閱
off();
c.set({ x: 3 });
assert('off() stops listener', received.x === 2); // 應該仍然是 2

// 4. reset
const c2 = createCore({ y: 10 });
c2.set({ y: 99 });
c2.reset();
assert('reset() restores initial state', c2.get().y === 10);

// 5. destroy
c2.destroy();
try { c2.get(); assert('get after destroy throws', false); }
catch (e) { assert('get after destroy throws', true); }

console.log(`\n${passed} passed, ${failed} failed`);
if (failed > 0) process.exit(1);
