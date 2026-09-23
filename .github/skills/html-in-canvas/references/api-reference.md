# HTML-in-Canvas API Reference

Source: https://html-in-canvas.dev/docs/api-reference/ and https://github.com/WICG/html-in-canvas
Always confirm against the live reference — this API is experimental.

---

## HTMLCanvasElement extensions

```webidl
partial interface HTMLCanvasElement {
  [CEReactions, Reflect] attribute boolean layoutSubtree;
  attribute EventHandler onpaint;
  void requestPaint();
  ElementImage captureElementImage(Element element);
  DOMMatrix getElementTransform((Element or ElementImage) element, DOMMatrix drawTransform);
};
```

| Member | Description |
|--------|-------------|
| `layoutSubtree` | Reflected as the `layoutsubtree` HTML attribute. Opts direct children into layout and hit testing. |
| `onpaint` | Handler for the `paint` event. |
| `requestPaint()` | Forces a `paint` event next frame even if nothing changed. Analogous to `requestAnimationFrame()`. |
| `captureElementImage(element)` | Transferable `ElementImage` snapshot for worker use. |
| `getElementTransform(element, drawTransform)` | CSS transform to sync DOM position with a 3D draw transform (WebGL/WebGPU). |

`OffscreenCanvas` also exposes `getElementTransform()`.

### Effects of `layoutsubtree` on direct children

- Participate in layout, hit testing, and the accessibility tree
- Rendering is **not visible** until drawn with `drawElementImage()`
- Each child creates a stacking context, becomes a containing block for its descendants, and has paint containment

---

## `drawElementImage()` — CanvasDrawElementImage mixin

Available on `CanvasRenderingContext2D` and `OffscreenCanvasRenderingContext2D`. Overloads mirror `drawImage()`:

| Signature | Behaviour |
|-----------|-----------|
| `(element, dx, dy)` | Draw at (dx, dy), auto-sized to on-screen proportions |
| `(element, dx, dy, dw, dh)` | Draw scaled to dw × dh |
| `(element, sx, sy, sw, sh, dx, dy)` | Draw a source sub-rect at (dx, dy) |
| `(element, sx, sy, sw, sh, dx, dy, dw, dh)` | Draw a source sub-rect scaled into the dest rect |

`element` may be an `Element` or an `ElementImage`.

**Returns:** `DOMMatrix` — apply to `element.style.transform` to sync the DOM position with the drawn position.

**Requirements**
- `layoutsubtree` set on the canvas
- `element` is a **direct child** of the canvas
- `element` has generated boxes (not `display: none`)

**Behaviour**
- The canvas current transform matrix (CTM) **is** applied
- CSS transforms on the element are **ignored for drawing** (but still affect hit testing)
- Overflow is clipped to the element's border box

**Snapshot semantics**
- Inside a `paint` handler → draws the current frame's snapshot
- Outside a `paint` handler → draws the previous frame's snapshot
- Before any snapshot exists → **throws**

---

## `paint` event

```webidl
[Exposed=Window]
interface PaintEvent : Event {
  constructor(DOMString type, optional PaintEventInit eventInitDict);
  readonly attribute FrozenArray<Element> changedElements;
};
```

- Fires once per frame, immediately after the browser's own Paint step (spec "Option C")
- `changedElements` — children whose rendering changed since the last paint
- CSS **transform** changes do **not** trigger paint (transforms are ignored for drawing)
- Canvas draw commands issued in `paint` appear in the **current** frame
- DOM changes made in `paint` appear in the **next** frame
- `canvas.requestPaint()` forces the event to fire

---

## WebGL

```webidl
partial interface WebGLRenderingContext {
  void texElementImage2D(GLenum target, GLint level, GLint internalformat,
                         GLenum format, GLenum type, (Element or ElementImage) element);
};
```

Parameters match `texImage2D`; the source is an element. Use `LINEAR` filtering for legible text.

## WebGPU

```webidl
partial interface GPUQueue {
  void copyElementImageToTexture((Element or ElementImage) source,
                                 GPUImageCopyTextureTagged destination);
};
```

Note: framework support for the WebGPU path may lag (e.g. PlayCanvas documents WebGL-only support). Check before choosing WebGPU.

---

## ElementImage

```webidl
[Exposed=(Window,Worker), Transferable]
interface ElementImage {
  readonly attribute unsigned long width;
  readonly attribute unsigned long height;
  undefined close();
};
```

Transfer to workers with `postMessage(msg, [elementImage])`. Call `close()` when finished to release resources.
