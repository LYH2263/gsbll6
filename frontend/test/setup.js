// Vitest 全局 setup：jsdom 环境下注入浏览器缺失的 API
import { vi } from 'vitest';

// jsdom 未实现 window.alert / matchMedia 等，组件里会调用 alert()
if (!globalThis.alert) {
  globalThis.alert = vi.fn();
}
if (!window.matchMedia) {
  window.matchMedia = () => ({
    matches: false,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  });
}
