---
name: graph-visualizer
description: "Builds a fully 3D interactive goal-graph visualization as a self-contained HTML file using Three.js. Use this skill whenever the user wants to visualize a goal, system, workflow, or project as an animated directed graph — with a 3D space background, glowing floating nodes, an animated pulse traveling the loop, and a collapsible constraints sidebar. Trigger when the user says things like 'create a graph for my goal', 'visualize my system as a graph', 'build a 3D graph app', 'show my workflow as a graph', or 'make an interactive graph visualization'. Parses natural language description of nodes, edges, weights, and constraints, and produces THREE distinct production-grade Three.js HTML files with different aesthetics."
---

# Graph Visualizer — Three.js Build Guide

Produces **THREE separate self-contained HTML files**, each with a distinct aesthetic direction. All JS inline. No build tools. Open in any browser.

---

## Before writing any code, read these skills

Read ALL of the following skills before writing a single line:

- `threejs-fundamentals` — scene, camera, renderer, clock, resize
- `threejs-geometry` — TubeGeometry for edges, Points for stars
- `threejs-materials` — MeshStandardMaterial, emissive glow
- `threejs-shaders` — ShaderMaterial for custom effects
- `threejs-postprocessing` — UnrealBloomPass
- `threejs-animation` — clock-driven pulse traversal
- `threejs-lighting` — point lights for node illumination
- `frontend-design` — aesthetic direction for each of the 3 variants

The `frontend-design` skill defines how to choose bold, distinctive, non-generic visual directions. Apply it to choose THREE meaningfully different themes (e.g. one dark/cyberpunk, one light/minimal, one warm/organic). Each variant must be genuinely distinct — different fonts, different color palettes, different node shapes, different edge styles.

---

## Step 1 — Parse the user's graph definition

Extract from the user's description:

```
GOAL_NODE     — final destination node (label + metric if given)
NODES[]       — { id, label, layer: 0..N, slot: 0..M, type: 'start'|'parallel'|'sequential'|'goal', weight: 'large'|'medium'|'small' }
EDGES[]       — { from, to, dashed?: boolean }
LOOP_PATH[]   — ordered node IDs the pulse travels (last entry loops back to first)
CONSTRAINTS[] — { id, label, type: 'time'|'energy'|'personal'|'market'|'economic'|'other', detail }
```

Nodes are laid out in layers along Y. Layer 0 = top (start), last layer = bottom (goal). Within a layer, nodes spread along X by slot.

---

## Step 2 — Design three aesthetic variants (from `frontend-design`)

Before any code, commit to 3 fully distinct aesthetic directions. Name them. Example sets (don't copy these — invent your own each time):

- **Variant A**: Dark cosmic / deep navy + electric cyan + gold, sharp geometric nodes, Syne font
- **Variant B**: Terminal green / pure black + phosphor green + white, monospace nodes, IBM Plex Mono font
- **Variant C**: Warm amber / dark brown + amber + cream, rounded organic nodes, Playfair Display font

Each variant gets its own HTML file. The graph data (nodes, edges, constraints) is identical — only the visual treatment changes.

**Per-variant specifications** — all variant-specific values throughout this skill come from this table:

| Element | Variant A (cosmic) | Variant B (terminal) | Variant C (warm) |
|---------|-------------------|---------------------|------------------|
| Stars | white, 3 dark-blue/purple nebula shells | green-tinted `0x88ffaa`, no nebula — pure black void | warm cream `0xffe8c0`, soft amber nebula shells |
| Node shape | BoxGeometry (sharp, geometric) | BoxGeometry extreme aspect ratio (wide/flat) | CylinderGeometry (rounded pill, laid flat) |
| Pulse color | cyan `0x6ee7f7` | bright green `0x39ff14` | amber/gold `0xfbbf24` |
| Lighting | themed ambient + key light colors per mood | themed ambient + key light colors per mood | themed ambient + key light colors per mood |

---

## Step 3 — Three.js scene setup (same for all variants, from `threejs-fundamentals`)

```javascript
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(60, W / H, 0.1, 200);
camera.position.set(0, 0, 18);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(W, H);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.enablePan = false;
controls.minDistance = 8;
controls.maxDistance = 40;
```

---

## Step 4 — Starfield background (from `threejs-geometry`)

~800 `THREE.Points` placed in a sphere of radius 60–80. Slowly rotate each frame. Apply variant-specific star colors and nebula settings.

**Checkpoint:** Open the HTML — verify the starfield renders on a blank canvas before proceeding to nodes.

---

## Step 5 — Node layout

```javascript
const LAYER_SPACING = 3.2;
const SLOT_SPACING  = 3.8;

function nodePosition(node) {
  const count = layerNodeCounts[node.layer];
  const x = (node.slot - (count - 1) / 2) * SLOT_SPACING;
  const y = -node.layer * LAYER_SPACING + (totalLayers - 1) * LAYER_SPACING / 2;
  return new THREE.Vector3(x, y, 0);
}
```

---

## Visibility Rules (referenced by Steps 6 and 7)

Past versions suffered from near-invisible nodes and edges on dark backgrounds. Apply these rules to all scene elements:

- **Base colors must NOT be near-black.** Use at minimum 15–25% lightness. E.g. `0x1a2a3a` not `0x020408`.
- **emissiveIntensity for nodes: 1.0–2.5** (not 0.3–0.5). Nodes should visibly glow.
- **Edge opacity: 0.7–0.9** for normal edges (not 0.45). Edge color must contrast the background.
- **Labels must be large and bright**: canvas size 512×128, font size 38–44px, white fill, dark shadow for contrast.

```javascript
// CORRECT — high visibility node
{ color: 0x0d2235,  emissive: 0x4a9eff, emissiveIntensity: 1.8, roughness: 0.4, metalness: 0.3 }

// WRONG — near-invisible
{ color: 0x080820, emissive: 0x4466ff, emissiveIntensity: 0.3, roughness: 0.6, metalness: 0.1 }
```

```javascript
// CORRECT — visible edge
new THREE.MeshBasicMaterial({ color: 0x1a5a8a, transparent: true, opacity: 0.75 })

// WRONG — invisible edge
new THREE.MeshBasicMaterial({ color: 0x1a3a4a, transparent: true, opacity: 0.45 })
```

---

## Step 6 — Node meshes (from `threejs-materials`)

Follow **Visibility Rules** above for all node materials and labels. Add a visible border/outline: create a slightly larger geometry behind each node with an emissive outline material, scaled by 1.05.

**Node sizes by weight:**
- `large`: 2.2 × 0.6 × 0.4
- `medium`: 1.8 × 0.55 × 0.4
- `small`: 1.4 × 0.5 × 0.4

**Outline glow mesh** (add behind each node):
```javascript
const outlineGeo = new THREE.BoxGeometry(dim.w * 1.08, dim.h * 1.2, dim.d * 0.5);
const outlineMat = new THREE.MeshBasicMaterial({ color: emissiveColor, transparent: true, opacity: 0.2 });
const outline = new THREE.Mesh(outlineGeo, outlineMat);
outline.position.copy(nodePos);
outline.position.z -= 0.05;
scene.add(outline);
```

Vary node shapes per variant.

**Checkpoint:** Open the HTML — confirm all nodes are clearly visible against the background and labels are readable before adding edges.

---

## Step 7 — Edges as tubes (from `threejs-geometry`)

Follow **Visibility Rules** above for all edge materials. Use the variant's accent color for edges (same hue as node glow but slightly desaturated).

Tube radius: `0.035` (not 0.025 — thicker is more visible).

For the feedback loop edge (goal → start): arc far left (X offset -10), opacity 0.4, dashed feel via alternating thin/thick segments if possible, otherwise just lower opacity.

---

## Step 8 — Animated pulse (from `threejs-animation`)

Build the full closed `CatmullRomCurve3` from LOOP_PATH bezier segments (30 points each).

Pulse sphere: `SphereGeometry(0.14, 16, 16)` — slightly larger than before (0.1 was too small).

```javascript
// emissiveIntensity must be high — this is the brightest element in the scene
new THREE.MeshStandardMaterial({ color: accentColor, emissive: accentColor, emissiveIntensity: 4.0 })
```

4–5 trail ghosts, decreasing size and emissiveIntensity. Loop duration: 8 seconds. Apply variant-specific pulse colors.

---

## Step 9 — Bloom (from `threejs-postprocessing`)

```javascript
const bloom = new UnrealBloomPass(
  new THREE.Vector2(W, H),
  1.2,   // strength — higher than before
  0.6,   // radius
  0.1    // threshold — very low so emissive materials bloom
);
```

---

## Step 10 — Lighting (from `threejs-lighting`)

```javascript
scene.add(new THREE.AmbientLight(variantAmbientColor, 3.0)); // brighter ambient than before
const key = new THREE.PointLight(variantKeyColor, 3.5, 40);
key.position.set(0, 6, 12);
scene.add(key);
```

Vary ambient and key light colors per variant to set mood.

**Checkpoint:** After adding bloom and lighting, verify the bloom effect is active — emissive nodes should have a visible glow halo in the rendered output.

---

## Step 11 — Constraints sidebar (HTML/CSS overlay)

Same data for all variants, but style it to match each variant's aesthetic.

```css
.constraints-panel {
  position: fixed; right: 0; top: 0;
  width: 280px; height: 100vh;
  background: variantPanelBg;     /* dark semi-transparent, themed to variant */
  backdrop-filter: blur(18px);
  border-left: 1px solid variantBorderColor;
  overflow-y: auto; z-index: 10;
  padding: 20px 12px;
  font-family: variantFont;
}
```

Accordion behavior: `max-height: 0 → 200px` CSS transition on `data-open` toggle.

Type badge colors (consistent across variants):
- `time` → amber `#f5c842`
- `energy` → cyan `#6ee7f7`
- `personal` → violet `#a78bfa`
- `market` → blue `#60a5fa`
- `economic` → red `#f87171`
- `other` → gray

---

## Step 12 — Resize, orbit controls

```javascript
window.addEventListener('resize', () => {
  const w = window.innerWidth - 280;
  const h = window.innerHeight;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h);
  composer.setSize(w, h);
});
```

---

## Step 13 — Animation loop

```javascript
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const delta  = clock.getDelta();
  const elapsed = clock.getElapsedTime();

  controls.update();
  stars.rotation.y += delta * 0.008;

  const t = (elapsed % LOOP_DURATION) / LOOP_DURATION;
  pulse.position.copy(fullPath.getPointAt(t));
  updateTrails(t);

  // Subtle node float
  nodeMeshes.forEach((item, i) => {
    item.mesh.position.y = item.mesh.userData.baseY + Math.sin(elapsed * 0.5 + i * 1.2) * 0.05;
    item.sprite.position.y = item.mesh.position.y;
    item.outline.position.y = item.mesh.position.y;
  });

  composer.render();
}
animate();
```

---

## Output

Save THREE files to `./`:
- `graph-[slug]-A.html` — Variant A
- `graph-[slug]-B.html` — Variant B
- `graph-[slug]-C.html` — Variant C

Call `present_files` with all three. Tell the user: "Here are 3 aesthetic variants — open each in any browser. Drag to orbit, scroll to zoom. Pick your favourite or ask for adjustments."

---

## Example invocations

> "Create a 3D graph for my quant finance goal — nodes are wake up/run, quant research, interview prep, exam prep, daily validation, social capital. Constraints: ADHD, time pressure, Singapore market."

> "Build a goal graph: morning routine → fitness / writing / networking → launch startup. Constraints: solo founder, 3-month runway."

---

## Critical rules

- **THREE HTML files** — always produce 3 variants, not 1.
- **Single HTML file per variant** — all CSS, JS, Three.js via importmap inline.
- **Use `<script type="importmap">`** for Three.js CDN.
- **Never use `localStorage`** — state in memory only.
- **Constraints panel is HTML/CSS** — not Three.js, canvas renders behind it.
- **Pulse loops seamlessly** — closed `CatmullRomCurve3` with `getPointAt(t)`.
- **Nodes must be VISIBLE** — emissiveIntensity ≥ 1.0, base color not near-black, outline glow mesh.
- **Edges must be VISIBLE** — opacity ≥ 0.7, tube radius ≥ 0.035, bright enough accent color.
- **Bloom threshold ≤ 0.15** — emissive materials must actually glow.
- **Pulse emissiveIntensity ≥ 3.5** — the pulse is the hero element, it must be unmistakably bright.
