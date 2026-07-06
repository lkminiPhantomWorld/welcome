/**
 * tiny-state-core
 * 最小化可組合狀態核心。
 * 可以掛載在任何地方。隨時卸載。
 * MIT 授權
 */

(function (root, factory) {
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = factory();
  } else if (typeof define === 'function' && define.amd) {
    define(factory);
  } else {
    root.TinyStateCore = factory();
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {

  function createCore(initialState) {
    var _state = Object.assign({}, initialState || {});
    var _listeners = {};  // 事件監聽器容器
    var _alive = true;    // 核心是否仍然活躍

    // 驗證核心是否已被銷毀
    function _assert() {
      if (!_alive) throw new Error('核心已被銷毀');
    }

    // 監聽事件
    function on(event, fn) {
      _assert();
      if (!_listeners[event]) _listeners[event] = [];
      _listeners[event].push(fn);
      // 返回一個卸載函數
      return function off() {
        _listeners[event] = (_listeners[event] || []).filter(function (f) { return f !== fn; });
      };
    }

    // 發出事件
    function emit(event, payload) {
      (_listeners[event] || []).forEach(function (fn) { fn(payload); });
    }

    // 獲取當前狀態的副本
    function get() {
      _assert();
      return Object.assign({}, _state);
    }

    // 更新狀態
    function set(patch) {
      _assert();
      _state = Object.assign({}, _state, patch);
      emit('change', Object.assign({}, _state));
    }

    // 重置為初始狀態
    function reset() {
      _assert();
      _state = Object.assign({}, initialState || {});
      emit('reset', Object.assign({}, _state));
    }

    // 銷毀核心
    function destroy() {
      emit('destroy', null);
      _listeners = {};
      _state = {};
      _alive = false;
    }

    return { on, get, set, reset, destroy };
  }

  return { createCore };
});
