/**
 * HTML-in-Canvas feature detection + fallback helper.
 * The API is experimental (Chromium, flag or origin trial). Always gate usage.
 */
export function detectHtmlInCanvas() {
  const canvasProto = HTMLCanvasElement.prototype;
  const ctx2dProto = window.CanvasRenderingContext2D?.prototype;
  const glProto = window.WebGLRenderingContext?.prototype;
  const gl2Proto = window.WebGL2RenderingContext?.prototype;

  return {
    layoutSubtree: 'layoutSubtree' in canvasProto,
    draw2d: !!ctx2dProto && 'drawElementImage' in ctx2dProto,
    requestPaint: 'requestPaint' in canvasProto,
    webgl:
      (!!glProto && 'texElementImage2D' in glProto) ||
      (!!gl2Proto && 'texElementImage2D' in gl2Proto),
    webgpu: !!window.GPUQueue && 'copyElementImageToTexture' in GPUQueue.prototype,
    worker: 'captureElementImage' in canvasProto,
  };
}

/** True when the requested capabilities are all present. */
export function supports(...caps) {
  const d = detectHtmlInCanvas();
  return caps.every((c) => d[c]);
}

/**
 * DOM-overlay fallback: moves canvas children out of the canvas into an
 * absolutely positioned overlay so they render and stay interactive.
 */
export function applyOverlayFallback(canvas) {
  canvas.removeAttribute('layoutsubtree');
  const wrapper = document.createElement('div');
  wrapper.style.position = 'relative';
  wrapper.style.display = 'inline-block';
  canvas.replaceWith(wrapper);
  wrapper.appendChild(canvas);

  const overlay = document.createElement('div');
  Object.assign(overlay.style, { position: 'absolute', inset: '0' });
  while (canvas.firstElementChild) overlay.appendChild(canvas.firstElementChild);
  wrapper.appendChild(overlay);
  return overlay;
}

/** Sizes the canvas grid to device pixels; re-requests paint on resize. */
export function observeDevicePixels(canvas, onResize) {
  const ro = new ResizeObserver(([entry]) => {
    const size = entry.devicePixelContentBoxSize?.[0];
    canvas.width = size ? size.inlineSize : Math.round(canvas.clientWidth * devicePixelRatio);
    canvas.height = size ? size.blockSize : Math.round(canvas.clientHeight * devicePixelRatio);
    onResize?.();
    canvas.requestPaint?.();
  });
  try {
    ro.observe(canvas, { box: 'device-pixel-content-box' });
  } catch {
    ro.observe(canvas);
  }
  return ro;
}
