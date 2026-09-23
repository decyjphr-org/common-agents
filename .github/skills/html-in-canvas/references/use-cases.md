# Use Cases and Design Patterns

## 1. Game UI and HUDs

**Problem:** Canvas games hand-draw menus with `fillText`, losing keyboard navigation, screen reader support, i18n, and CSS styling.

**Pattern:**
- Canvas with `layoutsubtree`; each menu/HUD panel is a direct child `<div>` with real `<button>`, `<input>`, `<select>` elements
- Game loop draws the scene, then `drawElementImage(hud, x, y)` on top, then syncs the transform
- Drive the loop with `canvas.requestPaint()` rather than a separate `requestAnimationFrame` draw
- Pairs well with the `game-engine` skill for the loop, physics, and input layers

**Watch for:** focus management when menus open/close; set `inert` on hidden panels.

## 2. Charts and data visualisation

**Problem:** Chart labels, legends, tooltips, and axis text rendered with `fillText` lack CSS typography and accessibility.

**Pattern:** Draw data marks with Canvas 2D or WebGL; draw legend/tooltip/axis `<div>`s with `drawElementImage`. Screen readers read the real legend and tooltip DOM.

## 3. Creative tools and editors

**Problem:** Rich text boxes in design tools require custom text layout engines.

**Pattern:** Each text box is a `contenteditable` direct child; apply canvas transforms (rotate/scale) to draw it within the artboard; sync the returned transform so the caret and selection land in the right place.

## 4. Shader effects on HTML

Ripple, blur, chromatic aberration, pixelation, page-curl, and transition effects applied to live UI via `texElementImage2D` + fragment shader. Keep interactive elements lightly distorted — hit testing follows the undistorted rectangle.

## 5. HTML in 3D scenes

Info panels, in-world screens, VR/AR-style UI rendered as textures on meshes. Use `getElementTransform` so pointer interaction maps onto the 3D surface.

## 6. Scene transitions

Blend two HTML scenes through a shader (crossfade, zoom-blur, wipe). Remotion uses this pattern for video transitions.

## 7. Media export

Draw HTML into a canvas, then `canvas.toBlob()` for images or `canvas.captureStream()` + `MediaRecorder` for video. Note the privacy exclusions — cross-origin images and iframes will not appear.

## 8. Accessibility retrofitting

Canvas apps that maintained a parallel hidden "fallback DOM" can replace it: the drawn element **is** the accessible element, so they never drift out of sync.

## 9. Replacing html2canvas

| html2canvas / foreignObject | HTML-in-Canvas |
|------------------------------|----------------|
| Reimplements CSS in JS; incomplete | Browser engine renders it; complete |
| Static snapshot | Live, redrawable every frame |
| Not interactive | Interactive and accessible |
| Slow for large DOM | Native speed |
| Cross-browser | Chromium-only today — keep html2canvas as fallback |
