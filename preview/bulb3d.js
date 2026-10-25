import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

/* Proper Electric - WebGL hero.
   Procedural A19 bulb, LED filament, scroll-driven parallax.
   Lives in its own column; never overlaps the copy. */

const GLASS_PROFILE = [
  [0.000, 1.000], [0.180, 0.993], [0.350, 0.965], [0.520, 0.910],
  [0.680, 0.820], [0.800, 0.700], [0.890, 0.550], [0.935, 0.380],
  [0.950, 0.190], [0.945, 0.000], [0.910, -0.180], [0.845, -0.330],
  [0.750, -0.450], [0.640, -0.545], [0.540, -0.625], [0.470, -0.700],
  [0.435, -0.770],
];
const BASE_PROFILE = [
  [0.436, -0.770], [0.452, -0.800], [0.455, -0.900], [0.452, -1.000],
  [0.448, -1.110], [0.432, -1.200], [0.400, -1.275], [0.350, -1.335],
];
const TIP_PROFILE = [
  [0.350, -1.335], [0.300, -1.390], [0.230, -1.450],
  [0.130, -1.500], [0.000, -1.520],
];

const GOLD = 0xd4901c;
const FILAMENT_GLOW = 0xffb347;
const ARC_COLOR = 0xffc87a;
const ARC_SETS = 6;

const toPts = (p) => p.map(([r, z]) => new THREE.Vector2(r, z));
const lerp = (a, b, t) => a + (b - a) * t;
const rand = (a, b) => a + Math.random() * (b - a);

/* Midpoint-displacement arc, same generator as the Blender scene.
   Tips are clamped inside the glass so nothing pokes through. */
function arcPoints(start, end, jitter, depth) {
  let pts = [start.clone(), end.clone()];
  for (let d = 0; d < depth; d++) {
    const out = [];
    for (let i = 0; i < pts.length - 1; i++) {
      const a = pts[i], b = pts[i + 1];
      const mid = a.clone().add(b).multiplyScalar(0.5);
      const len = a.distanceTo(b);
      mid.x += rand(-1, 1) * len * jitter;
      mid.y += rand(-1, 1) * len * jitter;
      mid.z += rand(-0.45, 0.45) * len * jitter;
      out.push(a, mid);
    }
    out.push(pts[pts.length - 1]);
    pts = out;
    jitter *= 0.62;
  }
  return pts;
}

function buildArcSet(material) {
  const set = new THREE.Group();
  const hub = new THREE.Vector3(0, 0.30, 0);

  for (let i = 0; i < 9; i++) {
    const a = (Math.PI * 2 * i) / 9 + rand(-0.35, 0.35);
    const reach = rand(0.52, 0.86);
    const tip = new THREE.Vector3(
      Math.cos(a) * reach,
      0.30 + Math.sin(a) * reach * 0.86,
      rand(-0.22, 0.22)
    );
    const pts = arcPoints(hub, tip, 0.17, 4);
    set.add(new THREE.Mesh(
      new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), pts.length * 2, rand(0.005, 0.011), 5),
      material
    ));

    const k = Math.floor(rand(pts.length / 3, pts.length - 3));
    const branchTip = pts[k].clone().add(new THREE.Vector3(rand(-0.26, 0.26), rand(-0.26, 0.26), rand(-0.12, 0.12)));
    const bp = arcPoints(pts[k], branchTip, 0.24, 3);
    set.add(new THREE.Mesh(
      new THREE.TubeGeometry(new THREE.CatmullRomCurve3(bp), bp.length * 2, 0.0035, 5),
      material
    ));
  }
  return set;
}

function studioEnv(renderer) {
  const c = document.createElement('canvas');
  c.width = 1024; c.height = 512;
  const g = c.getContext('2d');

  const grad = g.createLinearGradient(0, 0, 0, 512);
  grad.addColorStop(0.00, '#f7f8fa');
  grad.addColorStop(0.38, '#dfe1e7');
  grad.addColorStop(0.52, '#b7babf');
  grad.addColorStop(0.70, '#8f9197');
  grad.addColorStop(1.00, '#6d6f75');
  g.fillStyle = grad;
  g.fillRect(0, 0, 1024, 512);

  /* Tall soft rectangles. Their reflections become the long vertical
     highlight streaks you see down the side of a real studio bulb shot. */
  const box = (x, y, w, h, a) => {
    const r = g.createLinearGradient(x, y, x + w, y);
    r.addColorStop(0, 'rgba(255,255,255,0)');
    r.addColorStop(0.5, 'rgba(255,255,255,' + a + ')');
    r.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = r;
    g.fillRect(x, y, w, h);
  };
  box(150, 20, 120, 300, 1.0);
  box(640, 40, 86, 250, 0.85);
  box(860, 60, 60, 190, 0.5);

  const warm = g.createRadialGradient(430, 150, 10, 430, 150, 180);
  warm.addColorStop(0, 'rgba(255,232,196,0.9)');
  warm.addColorStop(1, 'rgba(255,232,196,0)');
  g.fillStyle = warm;
  g.fillRect(250, 0, 360, 330);

  g.fillStyle = 'rgba(28,30,36,0.55)';
  g.fillRect(0, 420, 1024, 92);

  const tex = new THREE.CanvasTexture(c);
  tex.mapping = THREE.EquirectangularReflectionMapping;
  tex.colorSpace = THREE.SRGBColorSpace;
  const pmrem = new THREE.PMREMGenerator(renderer);
  pmrem.compileEquirectangularShader();
  const env = pmrem.fromEquirectangular(tex).texture;
  pmrem.dispose();
  tex.dispose();
  return env;
}

/* The glass refracts the SCENE, not the HTML behind the canvas — so the
   studio backdrop has to be a real plane inside the scene. Its colours
   match the hero's CSS gradient so the seam is invisible. */
function backdrop() {
  const c = document.createElement('canvas');
  c.width = c.height = 1024;
  const g = c.getContext('2d');
  const base = g.createLinearGradient(0, 0, 0, 1024);
  base.addColorStop(0.00, '#d4d5da');
  base.addColorStop(0.46, '#e2e2e6');
  base.addColorStop(1.00, '#f3f3f5');
  g.fillStyle = base;
  g.fillRect(0, 0, 1024, 1024);
  const warm = g.createRadialGradient(512, 400, 20, 512, 400, 470);
  warm.addColorStop(0.00, 'rgba(255,214,154,0.60)');
  warm.addColorStop(0.55, 'rgba(255,226,186,0.20)');
  warm.addColorStop(1.00, 'rgba(255,226,186,0)');
  g.fillStyle = warm;
  g.fillRect(0, 0, 1024, 1024);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  const m = new THREE.Mesh(
    new THREE.PlaneGeometry(1, 1),
    new THREE.MeshBasicMaterial({ map: tex, toneMapped: false })
  );
  m.position.z = -7;
  return m;
}

function shadowSprite() {
  const c = document.createElement('canvas');
  c.width = c.height = 256;
  const g = c.getContext('2d');
  const grad = g.createRadialGradient(128, 128, 0, 128, 128, 128);
  grad.addColorStop(0.0, 'rgba(60,58,66,0.42)');
  grad.addColorStop(0.45, 'rgba(60,58,66,0.16)');
  grad.addColorStop(1.0, 'rgba(60,58,66,0)');
  g.fillStyle = grad;
  g.fillRect(0, 0, 256, 256);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  const m = new THREE.Mesh(
    new THREE.PlaneGeometry(3.4, 1.5),
    new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false })
  );
  m.rotation.x = -Math.PI / 2;
  m.position.y = -2.05;
  return m;
}

function glowSprite(size, color, opacity) {
  const c = document.createElement('canvas');
  c.width = c.height = 256;
  const g = c.getContext('2d');
  const grad = g.createRadialGradient(128, 128, 0, 128, 128, 128);
  grad.addColorStop(0.0, color.replace('ALPHA', '0.95'));
  grad.addColorStop(0.28, color.replace('ALPHA', '0.40'));
  grad.addColorStop(1.0, color.replace('ALPHA', '0'));
  g.fillStyle = grad;
  g.fillRect(0, 0, 256, 256);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  const s = new THREE.Sprite(new THREE.SpriteMaterial({
    map: tex, transparent: true, opacity,
    blending: THREE.AdditiveBlending, depthWrite: false, depthTest: true,
  }));
  s.scale.set(size, size, 1);
  return s;
}

export function createBulb(renderer, { lowPower = false, filamentStyle = 'tungsten' } = {}) {
  const group = new THREE.Group();
  const env = studioEnv(renderer);

  const glassMat = new THREE.MeshPhysicalMaterial({
    color: 0xffffff,
    metalness: 0,
    roughness: 0.0,
    transmission: 1,
    opacity: 1,
    transparent: true,
    thickness: 0.22,
    ior: 1.52,
    dispersion: 0.12,
    envMap: env,
    envMapIntensity: 1.35,
    clearcoat: 0.6,
    clearcoatRoughness: 0.02,
    reflectivity: 0.35,
    attenuationDistance: 6.0,
    attenuationColor: new THREE.Color(0xfff3e2),
    side: THREE.FrontSide,
  });

  const glass = new THREE.Mesh(new THREE.LatheGeometry(toPts(GLASS_PROFILE), 160), glassMat);
  group.add(glass);

  const nickel = new THREE.MeshPhysicalMaterial({
    color: 0xbcbdc2, metalness: 1, roughness: 0.22, envMap: env, envMapIntensity: 1.1,
  });
  group.add(new THREE.Mesh(new THREE.LatheGeometry(toPts(BASE_PROFILE), 96), nickel));

  const brass = new THREE.MeshPhysicalMaterial({
    color: 0xc79a4e, metalness: 1, roughness: 0.28, envMap: env, envMapIntensity: 1.1,
  });
  const collar = new THREE.Mesh(
    new THREE.LatheGeometry(toPts([[0.448, -0.772], [0.472, -0.792], [0.474, -0.848], [0.452, -0.866]]), 96),
    brass
  );
  group.add(collar);

  for (let i = 0; i < 6; i++) {
    const ring = new THREE.Mesh(new THREE.TorusGeometry(0.452, 0.016, 8, 72), nickel);
    ring.rotation.x = Math.PI / 2;
    ring.position.y = -0.90 - i * 0.072;
    group.add(ring);
  }

  group.add(new THREE.Mesh(
    new THREE.LatheGeometry(toPts(TIP_PROFILE), 96),
    new THREE.MeshPhysicalMaterial({ color: 0x0a0a0a, metalness: 0.1, roughness: 0.42, envMap: env })
  ));

  const goldMat = new THREE.MeshPhysicalMaterial({
    color: GOLD, metalness: 1, roughness: 0.3, envMap: env,
  });

  const stem = new THREE.Mesh(
    new THREE.LatheGeometry(toPts([
      [0.055, -0.70], [0.075, -0.55], [0.070, -0.30], [0.055, -0.12],
      [0.095, -0.06], [0.078, 0.00], [0.000, 0.02],
    ]), 32),
    glassMat
  );
  group.add(stem);

  const filament = new THREE.Group();
  const emissive = new THREE.MeshBasicMaterial({ color: 0xffd79a });

  if (filamentStyle === 'led') {
    const BRIDGE_Z = 0.62;
    [-0.195, -0.065, 0.065, 0.195].forEach((x) => {
      const stick = new THREE.Mesh(
        new THREE.CylinderGeometry(0.0115, 0.0115, BRIDGE_Z - 0.02, 12), emissive);
      stick.position.set(x, (BRIDGE_Z + 0.02) * 0.5, 0);
      filament.add(stick);
      [[0.02, -0.03], [BRIDGE_Z, BRIDGE_Z + 0.03]].forEach(([yEnd, yAnchor]) => {
        const curve = new THREE.CatmullRomCurve3([
          new THREE.Vector3(x, yEnd, 0),
          new THREE.Vector3(x * 0.55, (yEnd + yAnchor) * 0.5, 0),
          new THREE.Vector3(x * 0.16, yAnchor, 0),
        ]);
        filament.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 16, 0.008, 8), goldMat));
      });
    });
    filament.add(new THREE.Mesh(
      new THREE.LatheGeometry(toPts([[0, BRIDGE_Z + 0.06], [0.04, BRIDGE_Z + 0.03], [0.04, BRIDGE_Z - 0.02], [0, BRIDGE_Z - 0.04]]), 24),
      goldMat));
  } else {
    [-1, 1].forEach((sx) => {
      const curve = new THREE.CatmullRomCurve3([
        new THREE.Vector3(0.05 * sx, -0.04, 0),
        new THREE.Vector3(0.17 * sx, 0.10, 0),
        new THREE.Vector3(0.27 * sx, 0.22, 0),
        new THREE.Vector3(0.30 * sx, 0.30, 0),
      ]);
      filament.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 24, 0.009, 8), goldMat));
    });
    const coil = [];
    const turns = 22;
    for (let i = 0; i <= turns * 8; i++) {
      const t = i / (turns * 8);
      coil.push(new THREE.Vector3(
        -0.30 + 0.60 * t,
        0.30 + Math.cos(t * turns * Math.PI * 2) * 0.013,
        Math.sin(t * turns * Math.PI * 2) * 0.013
      ));
    }
    filament.add(new THREE.Mesh(
      new THREE.TubeGeometry(new THREE.CatmullRomCurve3(coil), 300, 0.007, 6), emissive));
  }
  group.add(filament);

  /* plasma: pre-build a handful of arc sets and cycle them, so the
     lightning re-strikes without rebuilding geometry every frame */
  const arcMat = new THREE.MeshBasicMaterial({
    color: ARC_COLOR, transparent: true, opacity: 0.9,
    blending: THREE.AdditiveBlending, depthWrite: false,
  });
  const arcSets = [];
  const setCount = lowPower ? 3 : ARC_SETS;
  for (let i = 0; i < setCount; i++) {
    const set = buildArcSet(arcMat);
    set.visible = i === 0;
    group.add(set);
    arcSets.push(set);
  }

  const core = glowSprite(1.15, 'rgba(255,182,88,ALPHA)', 0.5);
  core.position.y = 0.3;
  group.add(core);

  const halo = glowSprite(lowPower ? 3.0 : 3.8, 'rgba(255,198,124,ALPHA)', lowPower ? 0.07 : 0.10);
  halo.position.set(0, 0.25, -1.9);
  group.add(halo);

  const light = new THREE.PointLight(0xffb55c, 2.6, 8, 2);
  light.position.set(0, 0.3, 0);
  group.add(light);

  return { group, shadow: shadowSprite(), filament, core, halo, env, arcSets, arcMat };
}

export function mountHero(canvas, opts = {}) {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const lowPower = opts.lowPower ?? window.matchMedia('(max-width: 760px)').matches;

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
  } catch (e) {
    canvas.closest('[data-hero-stage]')?.setAttribute('data-webgl', 'failed');
    return null;
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, lowPower ? 1.25 : 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.88;
  renderer.outputColorSpace = THREE.SRGBColorSpace;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 100);
  camera.position.set(0, 0, 7.9);

  scene.add(new THREE.HemisphereLight(0xffffff, 0x9fa2ab, 1.1));
  const key = new THREE.DirectionalLight(0xffffff, 2.3);
  key.position.set(-4, 5, 6);
  scene.add(key);
  const rim = new THREE.DirectionalLight(0xcfd9f5, 2.4);
  rim.position.set(5, 2.5, -4);
  scene.add(rim);

  const back = backdrop();
  scene.add(back);

  const bulb = createBulb(renderer, { lowPower, filamentStyle: opts.filamentStyle || 'tungsten' });
  const pivot = new THREE.Group();
  pivot.add(bulb.group);
  scene.add(pivot);
  scene.add(bulb.shadow);

  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(new THREE.Vector2(1, 1), lowPower ? 0.22 : 0.34, 0.6, 0.90);
  composer.addPass(bloom);
  composer.addPass(new OutputPass());

  /* The canvas spans the whole hero so its in-scene backdrop IS the hero
     background — no visible canvas edge. The bulb is then offset into the
     right-hand column so it never sits under the copy. */
  let stacked = false;
  let homeX = 0, homeY = 0;
  function resize() {
    const r = canvas.getBoundingClientRect();
    if (!r.width || !r.height) return;
    renderer.setSize(r.width, r.height, false);
    composer.setSize(r.width, r.height);
    bloom.setSize(r.width, r.height);
    stacked = r.width < 980;
    camera.aspect = r.width / r.height;
    camera.fov = stacked ? 40 : 30;
    camera.updateProjectionMatrix();

    const vh = 2 * Math.tan((camera.fov * Math.PI) / 360) * camera.position.z;
    const vw = vh * camera.aspect;
    homeX = stacked ? 0 : vw * 0.255;
    homeY = stacked ? vh * 0.30 : 0;
    pivot.scale.setScalar(stacked ? 0.62 : 1);

    const dist = camera.position.z - back.position.z;
    const bh = 2 * Math.tan((camera.fov * Math.PI) / 360) * dist;
    back.scale.set(bh * camera.aspect * 1.3, bh * 1.3, 1);
  }
  resize();
  requestAnimationFrame(resize);
  new ResizeObserver(resize).observe(canvas);

  const stage = canvas.closest('[data-hero-stage]') || canvas.parentElement;
  let visible = true;
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; }, { rootMargin: '120px' })
    .observe(stage);

  let target = 0, current = 0, raf = 0;
  function readScroll() {
    const r = stage.getBoundingClientRect();
    const span = r.height + window.innerHeight;
    target = Math.min(Math.max((window.innerHeight - r.top) / span, 0), 1);
  }
  readScroll();
  current = target;
  window.addEventListener('scroll', readScroll, { passive: true });
  window.addEventListener('resize', readScroll, { passive: true });

  const start = performance.now();
  let activeSet = 0;
  let nextStrike = start + 120;
  function frame(now) {
    raf = requestAnimationFrame(frame);
    if (!visible) return;

    current = reduced ? target : lerp(current, target, 0.075);
    const p = current;
    const t = (now - start) / 1000;

    pivot.position.x = homeX;
    pivot.position.y = homeY + (reduced ? 0 : lerp(0.30, -0.44, p) + Math.sin(t * 0.7) * 0.045);
    pivot.rotation.y = reduced ? -0.18 : lerp(-0.42, 0.34, p);
    pivot.rotation.z = reduced ? 0 : lerp(0.06, -0.05, p);
    const base = stacked ? 0.62 : 1;
    pivot.scale.setScalar(base * (reduced ? 1 : lerp(1.02, 0.86, p)));

    bulb.shadow.position.x = homeX;
    bulb.shadow.position.y = -2.05 + homeY + pivot.position.y * 0.12;
    bulb.shadow.scale.setScalar(lerp(1.08, 0.86, p));
    bulb.shadow.material.opacity = lerp(0.95, 0.55, p);

    const flicker = reduced ? 1 : 0.94 + Math.sin(t * 11.3) * 0.025 + Math.sin(t * 4.1) * 0.035;
    bulb.core.material.opacity = 0.5 * flicker;
    bulb.halo.material.opacity = 0.10 * flicker;

    if (!reduced && now > nextStrike) {
      bulb.arcSets[activeSet].visible = false;
      activeSet = (activeSet + Math.floor(rand(1, bulb.arcSets.length))) % bulb.arcSets.length;
      bulb.arcSets[activeSet].visible = true;
      nextStrike = now + rand(70, 190);
    }
    bulb.arcMat.opacity = reduced ? 0.85 : 0.62 + Math.abs(Math.sin(t * 17.0)) * 0.38;

    composer.render();
  }
  raf = requestAnimationFrame(frame);

  stage.setAttribute('data-webgl', 'ready');

  return {
    destroy() {
      cancelAnimationFrame(raf);
      composer.dispose();
      renderer.dispose();
      bulb.env.dispose();
    },
  };
}
