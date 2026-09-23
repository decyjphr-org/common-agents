# Synchronization: Keeping DOM and Pixels Aligned

The most important and most-missed part of HTML-in-Canvas.

## Why it matters

An element inside a `layoutsubtree` canvas has two positions:

1. **Layout position** — where the browser thinks it is. Drives hit testing (clicks, hover), focus rings, IntersectionObserver, and the accessibility tree.
2. **Drawn position** — where you painted its pixels with `drawElementImage()`.

If these differ, users click on empty pixels to activate a button drawn somewhere else, and screen readers report the wrong location. **Synchronization makes the layout position match the drawn position.**

## 2D canvas

`drawElementImage()` returns the transform to apply:

```js
canvas.onpaint = () => {
  ctx.reset();
  const t = ctx.drawElementImage(el, x, y);
  el.style.transform = t.toString();
};
```

This works because CSS transforms on the element are **ignored for drawing** but **respected for hit testing**. You can freely set `transform` to the returned matrix without affecting what's drawn, and without triggering another paint (transform changes don't fire `paint`).

The canvas CTM is applied when drawing, so rotations/scales via `ctx.rotate()`, `ctx.scale()`, `ctx.translate()` are reflected in the returned matrix automatically.

## 3D (WebGL / WebGPU)

`texElementImage2D` returns nothing. Compute the sync transform yourself with:

```js
const cssTransform = canvas.getElementTransform(el, drawTransform);
el.style.transform = cssTransform.toString();
```

Where `drawTransform` is a `DOMMatrix` describing how the element's texture maps onto the canvas. For a typical model-view-projection pipeline:

1. **Convert the MVP matrix** from your GL library (column-major `Float32Array`) into a `DOMMatrix` — `new DOMMatrix(Array.from(mvp))` for 4×4.
2. **Normalize the element.** HTML is sized in CSS pixels (e.g. 200px); GL geometry is often a unit quad (0–1 or -1–1). Scale by `1/width, 1/height` first, or the element maps 200× too large.
3. **Map clip space to the canvas viewport.** Clip space is -1…1 with Y up; the canvas grid is 0…width/height with Y down. Apply a viewport matrix (scale by width/2, -height/2 and translate by width/2, height/2).

The spec's general formula:

```
T_origin⁻¹ · S_css_to_grid⁻¹ · T_draw · S_css_to_grid · T_origin
```

- `T_draw` = CTM · Translation(x, y) · Scale(destScale)
- `T_origin` = element's computed `transform-origin`
- `S_css_to_grid` = CSS pixels → canvas grid pixels

## Shader distortion caveat

Synchronization is an **affine/projective** mapping. If a fragment shader warps the texture non-linearly (ripple, fisheye, wave), hit testing follows the *undistorted* rectangle. For interactive elements under heavy distortion, either:
- keep the distortion small/transient (e.g. transitions), or
- disable pointer interaction while the effect is active, or
- apply distortion only to non-interactive decorative elements.

## Device pixel ratio

Mismatched canvas grid size and CSS size makes output blurry and skews `S_css_to_grid`. Always:

```js
new ResizeObserver(([entry]) => {
  canvas.width  = entry.devicePixelContentBoxSize[0].inlineSize;
  canvas.height = entry.devicePixelContentBoxSize[0].blockSize;
  canvas.requestPaint?.();
}).observe(canvas, { box: 'device-pixel-content-box' });
```

When drawing in CSS-pixel coordinates on a DPR-scaled grid, apply `ctx.scale(devicePixelRatio, devicePixelRatio)` after `ctx.reset()` so the returned transform accounts for it.

## Verification checklist

- [ ] Click every interactive element where it is **drawn** — does it respond?
- [ ] Tab through focusable elements — is the focus ring on the drawn element?
- [ ] Inspect with DevTools Accessibility pane — do bounding boxes match the drawn content?
- [ ] Resize the window and zoom the page — does sync survive?
