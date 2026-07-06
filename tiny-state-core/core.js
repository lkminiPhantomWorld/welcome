/**
 * tiny-state-core
 * 一個極簡、可組合的狀態核心。
 * 可掛載在任何地方。也可隨時卸載。
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
    var _listeners = {};
    var _alive = true;

    function _assert() {
      if (!_alive) throw new Error('core has been destroyed');
    }

    function on(event, fn) {
      _assert();
      if (!_listeners[event]) _listeners[event] = [];
      _listeners[event].push(fn);
      return function off() {
        _listeners[event] = (_listeners[event] || []).filter(function (f) { return f !== fn; });
      };
    }

    function emit(event, payload) {
      (_listeners[event] || []).forEach(function (fn) { fn(payload); });
    }

    function get() {
      _assert();
      return Object.assign({}, _state);
    }

    function set(patch) {
      _assert();
      _state = Object.assign({}, _state, patch);
      emit('change', Object.assign({}, _state));
    }

    function reset() {
      _assert();
      _state = Object.assign({}, initialState || {});
      emit('reset', Object.assign({}, _state));
    }

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
