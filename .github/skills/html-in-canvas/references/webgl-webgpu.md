# HTML as a GPU Texture (WebGL / WebGPU / 3D engines)

## Raw WebGL

```js
const gl = canvas.getContext('webgl2');
const tex = gl.createTexture();

canvas.onpaint = () => {
  gl.bindTexture(gl.TEXTURE_2D, tex);
  gl.texElementImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, panel);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); // LINEAR for legible text
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  drawScene();
  syncTransform(); // canvas.getElementTransform(panel, drawMatrix)
};
```

Guidance:
- Upload the texture **inside `paint`** so it reflects the current frame
- Prefer `LINEAR` filtering; avoid mipmaps for text unless the surface is viewed at steep angles
- Texture orientation can differ from your UV convention — if the result is upside down, flip V in the shader rather than guessing a pixel-store flag, and verify against the live spec
- Only re-upload when `event.changedElements` includes the element, unless you are animating via `requestPaint()`

## Raw WebGPU

```js
canvas.onpaint = () => {
  device.queue.copyElementImageToTexture(panel, { texture: gpuTexture });
  render();
};
```

Size `gpuTexture` to the element's snapshot size and include `COPY_DST | TEXTURE_BINDING | RENDER_ATTACHMENT` usage as required by the copy.

## Three.js

There may be no first-party integration. Pattern:

1. Create the renderer on a canvas that has `layoutsubtree` and contains the HTML panel as a direct child
2. Create a `THREE.Texture` and upload with `texElementImage2D` via `renderer.getContext()` bound to the texture's WebGL handle (`renderer.properties.get(texture).__webglTexture`), or wrap it in a small custom texture class
3. In `paint`, re-upload, then `renderer.render(scene, camera)`
4. Compute `drawTransform` from `camera.projectionMatrix × camera.matrixWorldInverse × mesh.matrixWorld`, normalized to the element size, then call `getElementTransform`

Internal property names in Three.js change between versions — confirm against the installed version.

## PlayCanvas

PlayCanvas documents built-in support (WebGL backend only):

```js
canvas.setAttribute('layoutsubtree', 'true');
if (device.supportsHtmlTextures) {
  texture.setSource(htmlElement);
} else {
  // fallback: DOM overlay or canvas rasterization
}
```

## Babylon.js / others

Check the framework docs for native support first. Otherwise follow the raw WebGL pattern via the engine's underlying GL context.

## Choosing WebGL vs WebGPU

| | WebGL | WebGPU |
|-|-------|--------|
| API | `texElementImage2D` | `queue.copyElementImageToTexture` |
| Framework support | Broader (PlayCanvas ships it) | Lagging in some frameworks |
| Recommendation | Default choice today | Use only if the whole app is WebGPU |
