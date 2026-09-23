---
name: html-in-canvas
description: 'Expert skill for the experimental HTML-in-Canvas web API — drawing live, accessible DOM elements directly into a <canvas>, WebGL texture, or WebGPU texture using the layoutsubtree attribute, drawElementImage(), texElementImage2D(), copyElementImageToTexture(), and the paint event. Use whenever the user wants to render HTML/CSS into a canvas, put real HTML UI (menus, HUDs, forms, rich text, chart labels) inside a canvas or 3D scene, apply shader effects to HTML elements, use HTML as a WebGL/Three.js texture, replace html2canvas or foreignObject screenshot hacks, export HTML as images or video frames, or mentions layoutsubtree, drawElementImage, requestPaint, captureElementImage, ElementImage, or chrome://flags/#canvas-draw-element — even if they do not name the API explicitly.'
---

# HTML-in-Canvas

Build canvas, WebGL, and WebGPU experiences that render **real, live, accessible DOM** instead of hand-drawn text and fake UI.

HTML-in-Canvas is a **WICG proposal** implemented in Chromium. It replaces DOM-screenshotting workarounds (`html2canvas`, SVG `foreignObject`) with three native primitives plus a worker helper. It is **experimental and unstable** — the API can change or be removed.

## When to use this skill

- Rendering styled HTML/CSS into a `<canvas>` (chart labels, rich text boxes, in-game menus, HUDs)
- Using HTML as a texture in WebGL, WebGPU, Three.js, Babylon.js, or PlayCanvas
- Applying GPU shader effects (distortion, blur, ripple, glitch, transitions) to live HTML
- Making canvas content accessible without maintaining a separate fallback DOM
- Exporting HTML content as images or video frames via canvas
- Migrating off `html2canvas` or `foreignObject` rasterisation
- Debugging blurry output, desynced hit testing, missing paints, or thrown `drawElementImage` errors

## When NOT to use this skill

- Plain canvas drawing with no HTML content → standard Canvas 2D / WebGL (see the `game-engine` skill)
- Production code that must work in all browsers **without** a fallback path — this API is Chromium-only and flag/origin-trial gated
- Server-side screenshotting → use Playwright/Puppeteer instead

---

## Step 0 — Always verify the live spec first

The API is a living explainer and changes frequently. Before writing non-trivial code, fetch the current docs and reconcile anything below that conflicts:

- Spec overview: `https://html-in-canvas.dev/docs/overview/`
- API reference (IDL): `https://html-in-canvas.dev/docs/api-reference/`
- Source explainer: `https://github.com/WICG/html-in-canvas`

If the live docs disagree with this skill or its references, **the live docs win**. Tell the user what changed.

---

## The API in one example

```html
<canvas id="c" layoutsubtree>
  <div id="content">Hello, canvas</div>
</canvas>
<script>
  const ctx = c.getContext('2d');
  c.onpaint = () => {
    ctx.reset();
    const t = ctx.drawElementImage(content, 0, 0);
    content.style.transform = t.toString(); // keep DOM + pixels in sync
  };
</script>
```

## The three primitives + one helper

| Primitive | What it does |
|-----------|-------------|
| `layoutsubtree` attribute | Opts the canvas's **direct children** into layout, hit testing, and the accessibility tree. Children are laid out but **invisible until drawn**. |
| `drawElementImage()` / `texElementImage2D()` / `copyElementImageToTexture()` | Draws a direct child into a 2D canvas / WebGL texture / WebGPU texture. The 2D version returns a `DOMMatrix` to sync the DOM position. |
| `paint` event | Fires when rendering of any child changes. `event.changedElements` lists them. `canvas.requestPaint()` forces one (like `requestAnimationFrame`). |
| `captureElementImage()` | Creates a transferable `ElementImage` snapshot for `OffscreenCanvas` in a worker. |

Full IDL and overloads: [references/api-reference.md](references/api-reference.md)

---

## The five rules you must always follow

These are the causes of nearly every broken HTML-in-Canvas implementation. Apply them to every piece of code you write.

1. **Direct children only.** The element passed to `drawElementImage()` must be a direct child of a canvas with `layoutsubtree`, and must have generated boxes (not `display: none`). Wrap deep content in one direct-child container.
2. **Draw inside `paint`.** Draw in the `paint` handler. Outside `paint`, you get the *previous* frame's snapshot; before the first snapshot, the call **throws**. For continuous animation, call `canvas.requestPaint()` each frame instead of a bare `requestAnimationFrame` draw loop.
3. **Always sync the transform.** Apply the returned `DOMMatrix` to `element.style.transform` (2D), or use `canvas.getElementTransform(element, drawTransform)` (WebGL/WebGPU). Without this, clicks, focus, and screen readers point at the wrong place.
4. **Size the canvas to device pixels.** Use a `ResizeObserver` with `box: 'device-pixel-content-box'`, or output is blurry.
5. **Always feature-detect and ship a fallback.** Never assume support. See [references/browser-support-and-fallbacks.md](references/browser-support-and-fallbacks.md).

Detailed explanation of each, plus the transform maths: [references/synchronization.md](references/synchronization.md)

---

## Choosing a rendering path

| Goal | Path | Template |
|------|------|----------|
| HTML drawn into a 2D canvas, composited with other drawing | Canvas 2D + `drawElementImage` | [assets/basic-2d.html](assets/basic-2d.html) |
| Animated / continuously redrawn HTML | Canvas 2D + `requestPaint()` loop | [assets/animated-2d.html](assets/animated-2d.html) |
| Shader effects on live HTML (ripple, blur, distortion) | WebGL + `texElementImage2D` | [assets/webgl-shader-effect.html](assets/webgl-shader-effect.html) |
| HTML on a surface in a 3D scene | WebGL/Three.js texture + `getElementTransform` | See [references/webgl-webgpu.md](references/webgl-webgpu.md) |
| Heavy drawing off the main thread | `OffscreenCanvas` + `captureElementImage` | [assets/offscreen-worker.html](assets/offscreen-worker.html) |
| Any path | Feature detection + fallback helper | [assets/feature-detect.js](assets/feature-detect.js) |

---

## Workflow

1. **Clarify the goal** — 2D compositing, shader effect, 3D texture, worker offload, or export? Pick the path from the table above.
2. **Check the live spec** (Step 0).
3. **Start from the matching template** in `assets/`. Do not rewrite the boilerplate from memory — the templates encode the five rules.
4. **Structure the DOM** — one direct-child container per drawn element; put all interactive/accessible content inside it.
5. **Implement the `paint` handler** — `ctx.reset()`, draw, sync transform.
6. **Add feature detection and a fallback** — typically: render the HTML normally as an overlay, or show a static image.
7. **Review against the pitfalls checklist** — [references/pitfalls.md](references/pitfalls.md).
8. **Tell the user how to test** — Chromium with `chrome://flags/#canvas-draw-element` enabled, or origin-trial registration for real users.

---

## Privacy constraints to design around

`drawElementImage()` intentionally **omits** privacy-sensitive content. Do not build features that depend on these being drawn:

- Cross-origin content (iframes, images, `url()` refs, SVG `<use>`)
- Visited-link styling
- System colours, themes, and preferences
- Spelling/grammar markers and pending autofill
- Subpixel text anti-aliasing

If a user reports "my image/iframe is blank in the canvas", check for cross-origin content first.

---

## Reference files

| File | Read when |
|------|-----------|
| [references/api-reference.md](references/api-reference.md) | You need exact IDL, overloads, return values, or snapshot semantics |
| [references/synchronization.md](references/synchronization.md) | Hit testing, focus, or accessibility is misaligned; implementing 3D transforms |
| [references/webgl-webgpu.md](references/webgl-webgpu.md) | Using HTML as a GPU texture, Three.js/Babylon/PlayCanvas integration |
| [references/browser-support-and-fallbacks.md](references/browser-support-and-fallbacks.md) | Feature detection, flags, origin trial, fallback strategies |
| [references/use-cases.md](references/use-cases.md) | Designing a solution — game UI, charts, editors, transitions, export |
| [references/pitfalls.md](references/pitfalls.md) | Debugging, code review, final checklist |

## Output expectations

When generating code with this skill:

- Produce a **single self-contained HTML file** for demos unless the user specifies a framework
- Include feature detection and a visible "unsupported" fallback in every demo
- Comment where each of the five rules is satisfied
- State clearly that the API is experimental and how to enable it
