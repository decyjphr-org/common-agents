# Pitfalls, Debugging, and Review Checklist

## Symptom → cause → fix

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `drawElementImage` throws | Called before any snapshot exists, or outside `paint` on the first frame | Draw inside `onpaint`; call `canvas.requestPaint()` to trigger the first one |
| `drawElementImage` throws / draws nothing | Element is not a **direct** child, or canvas lacks `layoutsubtree` | Move the element up one level or wrap content in a direct-child container |
| Nothing drawn, no error | Element has `display: none` or zero size | Use `visibility`/`opacity` or size the element |
| Content is blurry | Canvas grid not sized to device pixels | `ResizeObserver` with `device-pixel-content-box` |
| Clicks hit the wrong place | Transform not synced | Apply the returned `DOMMatrix` to `element.style.transform` |
| Focus ring in wrong place / screen reader bounds wrong | Same as above | Same as above; verify in DevTools Accessibility pane |
| Animation freezes | Relying on `paint` firing without changes | Call `canvas.requestPaint()` each frame |
| Setting `transform` doesn't redraw | Transform changes don't fire `paint` (by design) | Change position via draw arguments / CTM, not CSS transform |
| DOM change appears one frame late | DOM mutations inside `paint` apply next frame | Mutate DOM before paint (e.g. in input handlers), draw in paint |
| Image / iframe blank in canvas | Cross-origin content is excluded for privacy | Serve same-origin, or draw the image separately with `drawImage` |
| Visited link colours missing | Excluded for privacy | Don't rely on `:visited` styling |
| Works in Canary, not stable Chrome | Flag off or no origin-trial token; `requestPaint` missing on older builds | Enable flag / register origin trial; detect `requestPaint` |
| Upside-down WebGL texture | UV convention mismatch | Flip V in the shader |
| Text shimmer in 3D | Mipmapping / nearest filtering | Use `LINEAR` filtering; avoid mipmaps for text |
| Hover doesn't track the rippled pixels | Shader distortion isn't reflected in hit testing | Limit distortion on interactive elements |
| Memory grows in worker path | `ElementImage` never closed | Call `elementImage.close()` after drawing |
| Stale frame drawn | Called `drawElementImage` from `requestAnimationFrame` instead of `paint` | Move drawing into `onpaint` |

## Performance

- Redraw only what changed — use `event.changedElements`
- Don't `requestPaint()` every frame unless animating
- Keep drawn elements small; large full-page elements cost more to snapshot and upload
- For WebGL, avoid re-uploading textures that are not in `changedElements`
- Offload heavy canvas work to a worker with `captureElementImage` + `OffscreenCanvas`

## Code review checklist

- [ ] Live spec checked for API changes
- [ ] `layoutsubtree` set on the canvas
- [ ] Every drawn element is a direct child with generated boxes
- [ ] Drawing happens inside the `paint` handler
- [ ] `ctx.reset()` (or clear) at the start of each 2D paint
- [ ] Returned transform (2D) or `getElementTransform` (3D) applied to every drawn element
- [ ] Canvas sized to device pixels via `ResizeObserver`
- [ ] `requestPaint()` used for animation loops
- [ ] Feature detection covers every method the code calls
- [ ] Fallback experience implemented and tested in a non-supporting browser
- [ ] No reliance on cross-origin content, `:visited`, or system colours
- [ ] `ElementImage.close()` called in worker paths
- [ ] Interactive elements verified: click, tab focus, screen reader
- [ ] Experimental status and enablement steps documented for users
