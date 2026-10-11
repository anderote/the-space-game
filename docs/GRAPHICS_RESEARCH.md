# Graphics research and implementation priorities

Research date: 2026-10-11. Scope: improvements compatible with this game's existing orthographic Three.js/WebGL renderer, especially during long endless-wave sessions. This is a recommendation report, not a claim that these changes are implemented or benchmarked.

Inspected: `web/src/renderer.js`, the installed Three.js postprocessing sources, and `package.json` (`three ^0.180.0`). Public technical references below are official Three.js documentation or material written by the technique's authors. Current online documentation can describe newer Three.js versions; the installed package remains the compatibility authority.

## Findings in the current renderer

The renderer already has a useful foundation: an orthographic camera; extruded, lit structure silhouettes; procedural canvas textures; warm key and cool rim directional lights; ACES filmic tone mapping; a bloom composer; and a separate crisp Canvas2D tactical overlay.

Its current limits are concrete:

- `texture('rock')` supplies color speckles and painted craters but no normal, bump, or roughness texture. The markings cannot respond to the light direction.
- `nebulaTexture()` layers radial gradients and stars into one 1024-square image, then repeats it four times. It has limited filament structure and repeats recognizable patterns.
- Hull materials use high metalness, but there is no environment map. More metallic material does not by itself create rich reflected highlights.
- Lasers, explosions, mining beams, and projectiles are drawn on the Canvas2D overlay after the 3D pass. They bypass the scene's bloom and cannot illuminate nearby geometry.
- Each asteroid, enemy, and building creates multiple independent meshes and geometries. Individual glow materials are also allocated frequently.
- Every link performs two linear searches through `sim.buildings` each rendered frame. The overlay can become expensive as an endless-wave base grows.
- `antialias: true` is set on the WebGL renderer, while the high-quality path renders through the composer's offscreen target. That flag alone does not establish antialiasing of the offscreen scene.
- High/low quality currently switches the composer on or off. It does not provide independent budgets for internal resolution, particles, material detail, or light count.

These observations describe the inspected snapshot. Concurrent development may supersede specific details.

## Priority order

| Priority | Change | Visual impact | Compatibility and cost |
| --- | --- | --- | --- |
| 1 | Procedural asteroid height/normal/roughness fields plus stronger shape variation | High: rocks look geological and react to light | Fits existing MeshStandardMaterial and geometry generation; mostly creation-time work |
| 1 | Filamented nebula with a quiet center and sparse separate stars | High: replaces the largest flat/repetitive part of the image | One background shader or a cached generated texture; cap shader work |
| 1 | Material/lighting calibration and a static procedural environment map | High: clearer metal panels, depth, and rim separation | Generate PMREM once; no per-frame capture needed |
| 1 | Crisp HDR combat effects and a small pool of transient lights | High during battle: weapons feel connected to the scene | Reuse existing simulation effects; fixed pool and short lifetimes |
| 1 for endless mode | Reuse geometry/materials, instance small repeated ships and debris, eliminate link searches | Preserves all visual improvements under load | Some renderer refactoring; no simulation balance changes |
| 2 | Hull panel normal maps, vents, seams, wear, and upgrade markers | Medium/high at close zoom | Shared texture sets and merged static submeshes |
| 2 | Layered explosions, short trails, ore sparks, shield impact arcs | Medium/high during combat | Pooled particles with strict maximum counts |
| 2 | Offscreen antialiasing and adaptive resolution tiers | High edge quality and consistency | Tune against measured frame cost |
| 3 | Screen-space AO or additional post effects | Situational | Add only after direct materials/lighting and profiling; avoid obscuring tiny units |

The highest-value first pass is asteroid relief, nebula structure, metallic highlights, and scene-integrated combat light. Adding more bloom alone would make the existing flat areas brighter without providing the missing detail.

## Surface detail that survives the top-down camera

**Proposed asteroid generation:** create a seeded scalar height field combining broad ridges, medium crater rims, and restrained fine noise. Use the same field to derive color, bump or tangent-space normal, and roughness maps. Start with one shared 512-square set per rock family, three or four families, and varied rotation/tint/scale. Distort the coarse icosahedron silhouette separately; texture normals cannot change an object's outline.

Use larger geometric cracks and protrusions visible at normal zoom, not only tiny texture noise. Reserve bright green material for ore seams and clusters; lower their brightness and coverage as ore is depleted. Keep a visible exhausted remnant only if gameplay and selection rules explicitly support it.

Official material guidance: normal maps alter lighting normals rather than geometry; bump maps are ignored when a normal map is present; roughness maps use the green channel. Nonmetal stone should normally have metalness zero. These features are directly available on the current material class. [MeshStandardMaterial](https://threejs.org/docs/pages/MeshStandardMaterial.html)

Color textures and emissive textures use sRGB annotation. Normal, bump, and roughness textures store data and should use `NoColorSpace`. The existing helper assigns sRGB unconditionally, so split color-texture creation from data-texture creation before generating new maps. Keep the working scene linear and perform display conversion once. [Three.js color management](https://threejs.org/manual/pages/color-management.html)

**Proposed hull treatment:** use one original tileable panel texture set for plates, bevel highlights, seams, and sparse scratches. Separate painted surfaces from bare edges. Roughness variation is more useful here than making every part mirror-smooth. Retain each building's distinct top silhouette and colored functional core.

## Lighting and tone mapping

The existing warm/cool pair is appropriate for readable metal forms. First reduce overly uniform fill and compare it against a modest procedural environment. Build an environment scene containing broad dim colored sources and one brighter strip, bake it once with `PMREMGenerator.fromScene`, and assign the resulting texture as `scene.environment`. It need not appear as the visible sky. The PMREM API supports filtering an environment according to material roughness. [PMREMGenerator](https://threejs.org/docs/pages/PMREMGenerator.html)

**Starting art-direction experiment, not a physically calibrated preset:** lower ambient contribution, retain a warm upper-left key, and use a weaker cyan rim so unpowered hulls still read. Adjust exposure after the material inputs and lighting are correct. Do not compensate for incorrect texture color spaces by increasing lamp intensity.

Keep `RenderPass → UnrealBloomPass → OutputPass`. OutputPass handles tone mapping and display color conversion using renderer settings. Effects requiring sRGB input, such as FXAA, belong after OutputPass. [OutputPass](https://threejs.org/docs/pages/OutputPass.html)

Bloom's threshold controls which bright areas contribute, while strength and radius control the spread. Its mip chain already performs broad blurs at lower resolutions. Keep threshold around the current HDR range and raise emission on actual light sources selectively; do not force the nebula and every metal highlight to glow. Initial tuning candidates: strength 0.35–0.6, radius 0.25–0.5, threshold 1.0–1.25, compared at fixed exposure. These are project-specific proposals. [UnrealBloomPass](https://threejs.org/docs/pages/UnrealBloomPass.html)

The installed r180 composer creates half-float render targets, and its OutputPass supports ACES and AgX. Preserve ACES initially for consistency; compare AgX only with fixed reference screenshots. A pipeline change should not conceal regressions in team color or warning visibility. [Pinned r180 EffectComposer](https://github.com/mrdoob/three.js/blob/r180/examples/jsm/postprocessing/EffectComposer.js), [pinned r180 OutputPass](https://github.com/mrdoob/three.js/blob/r180/examples/jsm/postprocessing/OutputPass.js)

## Nebula and depth without a camera rewrite

Fractal Brownian motion sums noise over multiple scales. Domain warping perturbs the sampling coordinates and can create more organic cloud filaments. The authors demonstrate these techniques directly. [The Book of Shaders, chapter 13](https://thebookofshaders.com/13/?lan=en)

**Proposed background:** one inexpensive shader plane at the current background depth. Combine four octaves of noise with a single low-frequency coordinate warp. Shape the density into one or two broad diagonal cloud bands, then use a separate low-frequency mask for dark dust. Blend a subdued teal/blue/purple palette while leaving a darker region behind the mining field. Keep luminance well below units and links.

Bake the field once into a texture or low-resolution render target for the low quality tier. For high quality, either retain the cached image with mild parallax or animate only a low-frequency offset. Avoid a full-resolution, many-step volumetric raymarch: the fixed overhead view does not require that cost.

Separate stars from the cloud field. Use a small number of seeded point layers with slightly different parallax factors and brightness distributions. Parallax must be explicit: with an orthographic camera, putting geometry farther away does not automatically create perspective parallax. Keep stars dim near the active field and avoid star shapes that resemble projectiles. Freeze optional drift when reduced motion is enabled.

Custom uniforms fit the existing ShaderMaterial route. Update time or camera offsets without recreating shader programs. Preserve correct output conversion in the direct low-quality path as well as the composer path. [ShaderMaterial](https://threejs.org/docs/pages/ShaderMaterial.html)

## Combat effects that illuminate the battlefield

**Proposed incremental approach:** keep selection, range indicators, health bars, and essential beam cores in the crisp tactical overlay. Add pooled scene-space additive beam halos and explosion sprites beneath that overlay. This gives the composer HDR emission while retaining exact targeting readability. Emissive surfaces look bright but do not automatically light other objects in this forward-rendered setup.

Use at most four to six reused, non-shadow-casting point lights for the most significant nearby impacts. Weight by effect size and camera visibility; update their positions/intensity and return them to the pool after roughly 80–200 milliseconds. Pool size and lifetime are starting design values, not measured limits. Ordinary distant shots should use emissive sprites without individual lights.

Build explosions from three phases: short white-hot core; expanding colored shock ring; a few slower fading fragments. Give missile exhaust a narrow tapered trail and vary burst scale by ship type. Heavy THEL shots should remain narrow and continuous-looking, while Pulser fire should read as separated pulses. Preserve original mechanical distinctions even when the effects become richer.

## Endless-wave performance

1. Cache primitive geometry and shared materials. Merge static hull pieces by material within a structure; leave turrets independent. Shared resources need explicit ownership so deleting one ship does not dispose geometry still used by others. This changes the current `disposeGroup` assumptions.
2. Instance the common small-enemy hulls, thrusters, and debris. Keep complex motherships and selected structures as ordinary groups initially. InstancedMesh reduces draw calls when geometry and material are shared; update instance matrices/colors and mark the corresponding attributes dirty. Recalculate or conservatively maintain bounds when instance placement changes. [InstancedMesh](https://threejs.org/docs/pages/InstancedMesh.html)
3. Use a fixed-capacity effect pool and compact active arrays. Cull effects outside the camera, skip decorative spark particles below a projected-size threshold, and limit simultaneous shock rings. Never cap actual enemy simulation counts merely to meet a rendering budget.
4. Build an ID-to-building map once per rendered frame or share the engine's lookup map. Resolve each link in constant time rather than scanning the building list twice. Use analogous lookups for drone/repair/miner targets.
5. Measure render calls, triangles, texture/geometry counts, and CPU frame time. With the composer, set `renderer.info.autoReset = false`, collect counters over the complete frame, then reset once. Compile anticipated materials before the first large wave when possible. [WebGLRenderer](https://threejs.org/docs/pages/WebGLRenderer.html)

Three.js's optimization guide explains that many meshes and scene nodes incur overhead even when triangle counts are modest. Merging is useful for static geometry, while independently moving objects call for other strategies. [Optimize Lots of Objects](https://threejs.org/manual/pages/optimize-lots-of-objects.html)

### Quality tiers and verification

| Tier | Proposed policy |
| --- | --- |
| High | Capped internal pixel count, bloom, normal maps, restrained particle budget, transient light pool |
| Balanced | Reduced internal scale, cached nebula, same silhouettes and tactical overlay, smaller effects/light pool |
| Low | Direct renderer, cached nebula, no transient lights, minimal particles, all gameplay cues retained |

Use a pixel-count cap as well as a DPR cap. DPR 2 means four times the pixel work of DPR 1 at the same CSS dimensions; large Retina windows are expensive before any effects are added. Keep overlay text at its own crisp resolution while lowering the 3D buffer when needed. Update renderer, composer, and overlay sizes deliberately on resize and display changes. [Responsive Design](https://threejs.org/manual/pages/responsive.html)

For antialiasing, compare a multisampled composer target against a suitable postprocessing AA pass. The current renderer context flag does not enable samples on the composer's default target. Test on the actual installed version and device; do not assume the fastest choice. Avoid stacking multiple AA methods by default.

Acceptance scenes: quiet opening; full network at minimum zoom; close asteroid inspection; severe energy shortage; dense mixed fleet; overlapping explosions; and a long endless-wave soak with repeated spawn/despawn. Capture identical camera/seed/state before and after. Report measured frame times and stable memory counts rather than asserting that a technique is universally faster. Proposed target is a responsive 60 Hz desktop experience, with a graceful balanced tier; this research did not benchmark it.

## Primary art references

### Reassembly: readable silhouettes and concentrated energy

[Developer press kit](https://www.anisopteragames.com/press/) and [inspected screenshot](https://www.anisopteragames.com/press/images/8tVIjuH.png).

Direct visual observations: broad quiet background, clearly outlined modular forms, bright effects concentrated at weapons/impacts, and faction colors that remain recognizable in battle. Applicable direction: give ships a strong silhouette, dark surrounding space, and limited bright focal areas. Its dense neon combat is a reference for energy, not a reason to obscure this game's relay lines. No assets were copied into the repository.

### Space Haven: material detail and restrained functional glow

[Developer press kit](https://bugbyte.fi/press/) and [inspected screenshot](https://bugbyte.fi/press/images/01_design_and_build_1280x662.png).

Direct visual observations: cool industrial panels, warmer accent hardware, small local lights, and readable functional shapes. Applicable direction: separate painted plates, bare metal trim, and illuminated controls instead of giving the whole object one surface response. The isometric view itself is not a recommendation to change this game's orthographic map interaction.

Bugbyte's [background-generation devlog](https://bugbyte.fi/forums/showthread.php?tid=405) describes procedurally generating celestial backgrounds rather than storing them as sprites. This is useful precedent for original procedural art; it does not document an algorithm to reproduce.

Dyson Sphere Program was considered as a broader industrial-lighting reference, but no developer graphics implementation was inspected in this bounded pass. No specific rendering technique is attributed to it.
