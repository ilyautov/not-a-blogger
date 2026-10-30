# three.js 0.169.0 (subset)

Copied unmodified from the npm package `three@0.169.0` (`npm pack three@0.169.0`). License: MIT, see `LICENSE`.
Only the files the styles import are kept:

- `build/three.module.min.js`
- `examples/jsm/postprocessing/`: `EffectComposer.js`, `RenderPass.js`, `BokehPass.js`, `OutputPass.js`, `ShaderPass.js`, `MaskPass.js`, `Pass.js`
- `examples/jsm/shaders/`: `CopyShader.js`, `BokehShader.js`, `OutputShader.js`
- `examples/jsm/environments/RoomEnvironment.js`

Need another addon? Take it from the same version (`https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/...`) and
check its own imports: addons import each other by relative path.
