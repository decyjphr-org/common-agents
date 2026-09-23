# Browser Support, Feature Detection, and Fallbacks

Support status moves quickly. Re-check the live browser support page and the Chrome origin-trial announcement before stating availability to a user.

## Current status (verify before relying on this)

| Environment | How to enable |
|-------------|--------------|
| Chrome Canary / recent Chrome | `chrome://flags/#canvas-draw-element` → Enabled → restart |
| Brave (recent Chromium-based builds) | `brave://flags/#canvas-draw-element` |
| Real users on Chrome | Register for the **HTML-in-Canvas origin trial** (announced for Chrome 148–150) and add the trial token to your site |
| Firefox / Safari | Not supported — always use a fallback |

Older Chromium builds may expose `drawElementImage` but **not** `canvas.requestPaint()`. Code that animates or synchronizes frames needs both — detect both.

## Feature detection

```js
function detectHtmlInCanvas() {
  const canvasProto = HTMLCanvasElement.prototype;
  const ctx2dProto = window.CanvasRenderingContext2D?.prototype;
  const glProto = window.WebGLRenderingContext?.prototype;
  return {
    layoutSubtree: 'layoutSubtree' in canvasProto,
    draw2d: !!ctx2dProto && 'drawElementImage' in ctx2dProto,
    requestPaint: 'requestPaint' in canvasProto,
    webgl: !!glProto && 'texElementImage2D' in glProto,
    webgpu: !!window.GPUQueue && 'copyElementImageToTexture' in GPUQueue.prototype,
    worker: 'captureElementImage' in canvasProto,
  };
}
```

Check only the capabilities your path needs (e.g. 2D animation needs `layoutSubtree && draw2d && requestPaint`).

## Fallback strategies

| Strategy | When to use | Notes |
|----------|------------|-------|
| **DOM overlay** | Interactive UI (menus, forms, HUDs) | Remove `layoutsubtree`, absolutely position the HTML over the canvas. Keeps full interactivity; loses shader effects. Best default. |
| **Static image** | Decorative content, exports | Pre-rendered PNG/screenshot. Loses interactivity. |
| **Canvas `fillText` approximation** | Simple labels only | Loses rich CSS, RTL, complex scripts. |
| **`html2canvas` / `foreignObject`** | Legacy screenshot needs | Slow, incomplete CSS support, but works cross-browser. |
| **Unsupported message** | Demos and experiments | Tell users how to enable the flag. |

**Important:** when `layoutsubtree` is present but the API isn't implemented, children behave as normal canvas fallback content (not rendered). A DOM-overlay fallback must move the content **outside** the canvas or remove the attribute and restyle.

## Communicating status to users

Every demo or production integration should state:
- The API is experimental and may change or be removed
- Which browser/flag enables it
- What the fallback experience is
