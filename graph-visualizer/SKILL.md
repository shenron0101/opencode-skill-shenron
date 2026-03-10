---
name: graph-visualizer
description: >
  Builds a fully 3D interactive goal-graph visualization as a self-contained HTML file using Three.js. Use this skill whenever the user wants to visualize a goal, system, workflow, or project as an animated directed graph — with a 3D space background, glowing floating nodes, an animated pulse traveling the loop, and a collapsible constraints sidebar. Trigger when the user says things like "create a graph for my goal", "visualize my system as a graph", "build a 3D graph app", "show my workflow as a graph", or "make an interactive graph visualization". Parses natural language description of nodes, edges, weights, and constraints, and produces a production-grade Three.js HTML app.
---

# Graph Visualizer — Three.js Build Guide

Produces a **single self-contained HTML file**. All JS inline. No build tools. Opens in any browser.

---

## Before writing any code, read these skills

This skill depends on the following Three.js reference skills. Read them before coding:

- `threejs-fundamentals` — scene, camera, renderer, clock, resize
- `threejs-geometry` — node shapes, TubeGeometry for edges, Points for stars
- `threejs-materials` — MeshStandardMaterial, emissive glow, transparency
- `threejs-shaders` — ShaderMaterial for custom pulse/glow effects
- `threejs-postprocessing` — UnrealBloomPass for node and pulse bloom
- `threejs-animation` — clock-driven pulse traversal along path
- `threejs-lighting` — ambient + point lights for node illumination

Import Three.js and addons from CDN using importmap:
```html
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
  }
}
</script>
<script type="module">
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
</script>
```

---

## Step 1 — Parse the user's graph definition

Extract from the user's description:

```
GOAL_NODE     — final destination node (label + metric if given)
NODES[]       — { id, label, layer: 0..N, slot: 0..M, type: 'start'|'parallel'|'sequential'|'goal', weight: 'large'|'medium'|'small' }
EDGES[]       — { from, to, dashed?: boolean }
LOOP_PATH[]   — ordered node IDs for the animated pulse (must end back at start to close the loop)
CONSTRAINTS[] — { id, label, type: 'time'|'energy'|'personal'|'market'|'economic'|'other', detail }
```

Nodes are laid out in layers along the Y axis. Layer 0 = top (start node), last layer = bottom (goal node). Within a layer, nodes are spread along X by slot index.

---

## Step 2 — Scene setup (from `threejs-fundamentals`)

```javascript
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x020610);

const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 200);
camera.position.set(0, 0, 18);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.enablePan = false;
controls.minDistance = 8;
controls.maxDistance = 40;
```

---

## Step 3 — Space background starfield (from `threejs-geometry`)

Use `THREE.Points` with `THREE.BufferGeometry`. Place ~800 stars at random positions within a sphere of radius 80. Use `PointsMaterial({ size: 0.15, sizeAttenuation: true, color: 0xffffff })`. Slowly rotate the group each frame: `stars.rotation.y += delta * 0.008`.

Also add 2–3 large sphere shells with `MeshBasicMaterial({ color: 0x110033, transparent: true, opacity: 0.015, side: THREE.BackSide })` at radii 50–70 for nebula depth.

---

## Step 4 — Node 3D positions

```javascript
const LAYER_SPACING = 3.2;
const SLOT_SPACING  = 3.8;

function nodePosition(node, layerNodeCounts, totalLayers) {
  const count = layerNodeCounts[node.layer];
  const x = (node.slot - (count - 1) / 2) * SLOT_SPACING;
  const y = -node.layer * LAYER_SPACING + (totalLayers - 1) * LAYER_SPACING / 2;
  return new THREE.Vector3(x, y, 0);
}
```

---

## Step 5 — Node meshes (from `threejs-geometry` + `threejs-materials`)

Use `THREE.BoxGeometry` with scale to create pill-like nodes. Sizes by weight:
- `large`: 2.0 × 0.55 × 0.35
- `medium`: 1.6 × 0.5 × 0.35
- `small`: 1.3 × 0.45 × 0.35

Materials by node type (`MeshStandardMaterial`):
```javascript
goal:       { color: 0x1a1200, emissive: 0xf5c842, emissiveIntensity: 0.8, roughness: 0.3, metalness: 0.4 }
start:      { color: 0x001a18, emissive: 0x6ee7f7, emissiveIntensity: 0.5, roughness: 0.5, metalness: 0.2 }
parallel:   { color: 0x080820, emissive: 0x4466ff, emissiveIntensity: 0.3, roughness: 0.6, metalness: 0.1 }
gate:       { color: 0x120a1a, emissive: 0xa78bfa, emissiveIntensity: 0.4, roughness: 0.5, metalness: 0.2 }
```

Add node label as a canvas texture sprite:
1. Create offscreen canvas, write label text with Syne/sans-serif font
2. `new THREE.CanvasTexture(canvas)` → `SpriteMaterial({ map, transparent: true })`
3. `new THREE.Sprite(spriteMaterial)` positioned slightly in front of node (z + 0.3), scaled to fit

---

## Step 6 — Edges as tubes (from `threejs-geometry`)

For each edge, build a `THREE.CubicBezierCurve3` between the two node positions. Control points: offset Y by ±30% of the distance, offset Z slightly for depth variation.

```javascript
const curve = new THREE.CubicBezierCurve3(
  fromPos,
  new THREE.Vector3(fromPos.x, fromPos.y - dy * 0.4, fromPos.z + 0.8),
  new THREE.Vector3(toPos.x,   toPos.y   + dy * 0.4, toPos.z   + 0.8),
  toPos
);
const tube = new THREE.TubeGeometry(curve, 20, 0.025, 6, false);
const mat  = new THREE.MeshBasicMaterial({ color: 0x1a3a4a, transparent: true, opacity: 0.45 });
scene.add(new THREE.Mesh(tube, mat));
```

For the feedback loop edge (goal → start), arc far out to the left (offset X by −8) to visually wrap around the graph. Use lower opacity (0.25) and a slightly warmer color (0x2a1a0a).

---

## Step 7 — Animated pulse (from `threejs-animation`)

Build a full closed path by concatenating bezier curves for each consecutive pair in `LOOP_PATH`:

```javascript
const allPoints = [];
for (let i = 0; i < LOOP_PATH.length; i++) {
  const from = nodePositions[LOOP_PATH[i]];
  const to   = nodePositions[LOOP_PATH[(i + 1) % LOOP_PATH.length]];
  const curve = new THREE.CubicBezierCurve3(from, cp1, cp2, to); // same control points as edge
  allPoints.push(...curve.getPoints(40));
}
const fullPath = new THREE.CatmullRomCurve3(allPoints, true); // closed = true
```

Pulse mesh: `SphereGeometry(0.1, 12, 12)` with `MeshStandardMaterial({ color: 0x6ee7f7, emissive: 0x6ee7f7, emissiveIntensity: 3.0 })`.

Animate:
```javascript
const LOOP_DURATION = 8; // seconds
const t = (elapsed % LOOP_DURATION) / LOOP_DURATION;
pulse.position.copy(fullPath.getPointAt(t));
```

Trail ghosts: 4 spheres at `t - i*0.009` each, with `emissiveIntensity` and `scale` decreasing linearly. Update every frame.

---

## Step 8 — Bloom (from `threejs-postprocessing`)

```javascript
const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));

const bloom = new UnrealBloomPass(
  new THREE.Vector2(window.innerWidth, window.innerHeight),
  0.9,   // strength
  0.5,   // radius
  0.15   // threshold — low so emissive nodes glow
);
composer.addPass(bloom);
```

Use `composer.render()` in the animation loop instead of `renderer.render()`.

---

## Step 9 — Lighting (from `threejs-lighting`)

```javascript
scene.add(new THREE.AmbientLight(0x111133, 2.5));

const key = new THREE.PointLight(0x6688ff, 2.5, 35);
key.position.set(0, 6, 10);
scene.add(key);

const fill = new THREE.PointLight(0x331166, 1.2, 28);
fill.position.set(-10, -4, 6);
scene.add(fill);
```

---

## Step 10 — Constraints sidebar (HTML overlay, not Three.js)

Pure HTML/CSS overlay on top of the canvas. `position: fixed`, right-anchored, full height.

```css
.constraints-panel {
  position: fixed; right: 0; top: 0;
  width: 280px; height: 100vh;
  background: rgba(4, 6, 18, 0.8);
  backdrop-filter: blur(18px);
  border-left: 1px solid rgba(255,255,255,0.07);
  overflow-y: auto; z-index: 10;
  padding: 20px 12px;
  font-family: 'DM Sans', sans-serif;
}
```

Accordion: each item has a header (click to toggle `data-open`) and a body with `max-height: 0 → 200px` CSS transition.

Type badge colors: `time`=amber, `energy`=cyan, `personal`=violet, `market`=blue, `economic`=red, `other`=gray.

Also shift the Three.js canvas: `renderer.domElement.style.width = 'calc(100vw - 280px)'` and update camera aspect on resize.

---

## Step 11 — Resize

```javascript
window.addEventListener('resize', () => {
  const w = window.innerWidth - 280; // account for sidebar
  const h = window.innerHeight;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h);
  composer.setSize(w, h);
});
```

---

## Step 12 — Animation loop

```javascript
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const delta  = clock.getDelta();
  const elapsed = clock.getElapsedTime();

  controls.update();
  stars.rotation.y += delta * 0.008;

  // pulse
  const t = (elapsed % LOOP_DURATION) / LOOP_DURATION;
  pulse.position.copy(fullPath.getPointAt(t));
  updateTrails(t, elapsed);

  // subtle node float
  nodes.forEach((n, i) => {
    n.mesh.position.y = n.baseY + Math.sin(elapsed * 0.5 + i * 1.2) * 0.05;
  });

  composer.render();
}
animate();
```

---

## Output

Save as `graph-[goal-slug].html` to `/mnt/user-data/outputs/`. Call `present_files`. Tell the user: "Open in any browser — no server needed. Drag to orbit, scroll to zoom."

---

## Example invocations

> "Create a 3D graph for my quant finance goal — nodes are wake up/run, quant research, interview prep, exam prep, daily validation, social capital. Constraints: ADHD, context switching, time pressure, Singapore market."

> "Build a goal graph: start = morning routine, parallel = fitness / writing / networking, goal = launch my startup. Constraints: solo founder, 3-month runway, no funding."

> "Visualize my trading system as a 3D graph — signal generation → risk filter → execution → PnL validation → loop back. Constraints: latency, API rate limits."

---

## Critical rules

- **Single HTML file** — all CSS, JS, Three.js via importmap. No bundler.
- **Use `<script type="importmap">`** for Three.js CDN — required for ES module imports.
- **Never use `localStorage`** — all state in memory.
- **Constraints panel is HTML/CSS** — not Three.js. Canvas renders behind it.
- **Pulse loops seamlessly** — use `getPointAt(t)` on a closed `CatmullRomCurve3`.
- **Bloom threshold must be low** (≤ 0.2) so emissive materials actually glow.
- **Camera starts with a good default view** — all nodes visible, not too zoomed in.
