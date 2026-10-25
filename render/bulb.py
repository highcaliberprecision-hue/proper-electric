"""
Proper Electric - hero bulb render.
Photoreal A19 bulb, glass envelope, E26 metal base, plasma arcing inside.

Run inside Blender:  blender --background --python render/bulb.py
or paste into the Scripting tab and hit Run.

Set MODE below: 'light' | 'dark' | 'transparent'
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector

MODE = 'light'
FILAMENT = 'led'
TILT_DEG = 0.0
ORBIT = False
RES_X, RES_Y = 1920, 1080
SAMPLES = 160
OUT = '//hero-bulb-' + MODE + '-' + FILAMENT + '.png'

GOLD = (1.0, 0.66, 0.22, 1.0)
ARC_COLOR = (1.0, 0.82, 0.45, 1.0)
SEED = 7

random.seed(SEED)


# ---------- scene reset ----------

def wipe():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mat(name, **kw):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    for k, v in kw.items():
        if k in bsdf.inputs:
            bsdf.inputs[k].default_value = v
    return m


def emission_mat(name, color, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = color
    em.inputs['Strength'].default_value = strength
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
    return m


# ---------- revolved profiles ----------

GLASS_PROFILE = [
    (0.000, 1.000), (0.180, 0.993), (0.350, 0.965), (0.520, 0.910),
    (0.680, 0.820), (0.800, 0.700), (0.890, 0.550), (0.935, 0.380),
    (0.950, 0.190), (0.945, 0.000), (0.910, -0.180), (0.845, -0.330),
    (0.750, -0.450), (0.640, -0.545), (0.540, -0.625), (0.470, -0.700),
    (0.435, -0.770),
]

BASE_PROFILE = [
    (0.436, -0.770), (0.452, -0.800), (0.455, -0.900), (0.452, -1.000),
    (0.448, -1.110), (0.432, -1.200), (0.400, -1.275), (0.350, -1.335),
]

TIP_PROFILE = [
    (0.350, -1.335), (0.300, -1.390), (0.230, -1.450),
    (0.130, -1.500), (0.000, -1.520),
]


def revolve(profile, name, segments=96, solid=0.0):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    rings = []
    for r, z in profile:
        ring = []
        if r < 1e-5:
            ring = [bm.verts.new((0.0, 0.0, z))] * segments
        else:
            for i in range(segments):
                a = 2.0 * math.pi * i / segments
                ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z)))
        rings.append(ring)

    for a_ring, b_ring in zip(rings, rings[1:]):
        for i in range(segments):
            j = (i + 1) % segments
            quad = [a_ring[i], a_ring[j], b_ring[j], b_ring[i]]
            uniq = []
            for v in quad:
                if v not in uniq:
                    uniq.append(v)
            if len(uniq) >= 3:
                try:
                    bm.faces.new(uniq)
                except ValueError:
                    pass

    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()

    obj.modifiers.new('smooth', 'SUBSURF').levels = 2
    obj.modifiers['smooth'].render_levels = 2
    if solid:
        s = obj.modifiers.new('thickness', 'SOLIDIFY')
        s.thickness = solid
        s.offset = 1.0
    for p in mesh.polygons:
        p.use_smooth = True
    return obj


# ---------- plasma arcs ----------

def arc_points(start, end, jitter, depth):
    pts = [Vector(start), Vector(end)]
    for _ in range(depth):
        out = []
        for a, b in zip(pts, pts[1:]):
            mid = (a + b) * 0.5
            d = (b - a).length
            mid += Vector((
                random.uniform(-1, 1),
                random.uniform(-0.35, 0.35),
                random.uniform(-1, 1),
            )) * d * jitter
            out.extend([a, mid])
        out.append(pts[-1])
        pts = out
        jitter *= 0.62
    return pts


def make_arc(pts, name, radius):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radius
    cu.bevel_resolution = 2
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p.x, p.y, p.z, 1.0)
    obj = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(obj)
    return obj


def build_plasma(parent_mat):
    hub = Vector((0.0, 0.0, 0.30))
    arcs = []
    for i in range(9):
        a = 2.0 * math.pi * i / 9 + random.uniform(-0.3, 0.3)
        reach = random.uniform(0.45, 0.80)
        tip = Vector((
            math.cos(a) * reach,
            random.uniform(-0.25, 0.25),
            0.30 + math.sin(a) * reach * 0.85,
        ))
        pts = arc_points(hub, tip, 0.16, 5)
        arcs.append(make_arc(pts, 'arc_%d' % i, random.uniform(0.004, 0.009)))

        for b in range(random.randint(1, 2)):
            k = random.randint(len(pts) // 3, len(pts) - 3)
            branch_tip = pts[k] + Vector((
                random.uniform(-0.3, 0.3),
                random.uniform(-0.15, 0.15),
                random.uniform(-0.3, 0.3),
            ))
            bp = arc_points(pts[k], branch_tip, 0.22, 3)
            arcs.append(make_arc(bp, 'arc_%d_%d' % (i, b), 0.0035))

    for o in arcs:
        o.data.materials.append(parent_mat)
    return arcs


# ---------- filament ----------

def build_filament(gold_mat, glass_mat, emissive):
    """LED filament sticks (reference sheet) or a classic tungsten coil."""
    stem = revolve(
        [(0.055, -0.70), (0.075, -0.55), (0.070, -0.30), (0.055, -0.12),
         (0.095, -0.06), (0.078, 0.00), (0.000, 0.02)],
        'stem', 48,
    )
    stem.data.materials.append(glass_mat)

    parts = [stem]

    if FILAMENT == 'led':
        bridge_z = 0.62
        bridge = revolve(
            [(0.000, bridge_z + 0.03), (0.040, bridge_z), (0.040, bridge_z - 0.05),
             (0.000, bridge_z - 0.07)],
            'bridge', 24,
        )
        bridge.data.materials.append(gold_mat)
        parts.append(bridge)

        for i, x in enumerate((-0.195, -0.065, 0.065, 0.195)):
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.0115, depth=bridge_z - 0.02,
                location=(x, 0.0, (bridge_z + 0.02) * 0.5),
                vertices=16,
            )
            stick = bpy.context.object
            stick.name = 'led_%d' % i
            stick.data.materials.append(emissive)
            parts.append(stick)

            for z_end, z_start in ((0.02, -0.04), (bridge_z, bridge_z - 0.04)):
                lead = make_arc(
                    [Vector((x, 0, z_end)),
                     Vector((x * 0.55, 0, z_start + (0.06 if z_end < 0.3 else -0.06))),
                     Vector((x * 0.18, 0, z_start))],
                    'lead_%d_%.2f' % (i, z_end), 0.008)
                lead.data.materials.append(gold_mat)
                parts.append(lead)
    else:
        for sx in (-1, 1):
            w = make_arc([
                Vector((0.055 * sx, 0, -0.05)), Vector((0.16 * sx, 0, 0.08)),
                Vector((0.27 * sx, 0, 0.20)), Vector((0.30 * sx, 0, 0.29)),
            ], 'wire_%d' % sx, 0.010)
            w.data.materials.append(gold_mat)
            parts.append(w)

        coil = []
        turns = 26
        for i in range(turns * 8 + 1):
            t = i / (turns * 8)
            coil.append(Vector((
                -0.30 + 0.60 * t,
                math.sin(t * turns * 2 * math.pi) * 0.012,
                0.295 + math.cos(t * turns * 2 * math.pi) * 0.012,
            )))
        c = make_arc(coil, 'coil', 0.0075)
        c.data.materials.append(emissive)
        parts.append(c)

    return parts


def build_orbit(emissive):
    """Thin light streak circling the bulb, as in the reference sheet."""
    pts = []
    for i in range(129):
        t = i / 128.0
        a = t * 2.0 * math.pi
        pts.append(Vector((
            math.cos(a) * 1.55,
            math.sin(a) * 0.95,
            0.05 + math.sin(a) * 0.52,
        )))
    ring = make_arc(pts, 'orbit', 0.006)
    ring.data.materials.append(emissive)
    return ring


# ---------- build ----------

wipe()
scene = bpy.context.scene

glass = mat('glass', **{
    'Base Color': (1.0, 0.98, 0.95, 1.0),
    'Roughness': 0.02,
    'Metallic': 0.0,
    'IOR': 1.45,
})
glass.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value = 1.0

nickel = mat('nickel', **{
    'Base Color': (0.74, 0.74, 0.76, 1.0),
    'Metallic': 1.0,
    'Roughness': 0.24,
})

brass = mat('brass_collar', **{
    'Base Color': (0.78, 0.58, 0.28, 1.0),
    'Metallic': 1.0,
    'Roughness': 0.30,
})

black = mat('insulator', **{
    'Base Color': (0.03, 0.03, 0.03, 1.0),
    'Roughness': 0.38,
    'Metallic': 0.0,
})

gold = mat('filament_gold', **{
    'Base Color': GOLD,
    'Metallic': 1.0,
    'Roughness': 0.30,
})

plasma = emission_mat('plasma', ARC_COLOR, 55.0)

envelope = revolve(GLASS_PROFILE, 'envelope', 128, solid=0.012)
envelope.data.materials.append(glass)

base = revolve(BASE_PROFILE, 'base', 96)
base.data.materials.append(nickel)

threads = base.modifiers.new('threads', 'DISPLACE')
tex = bpy.data.textures.new('thread_wave', 'WOOD')
tex.wood_type = 'RINGS'
tex.noise_scale = 0.06
threads.texture = tex
threads.strength = 0.012
threads.mid_level = 0.5

collar = revolve(
    [(0.448, -0.772), (0.470, -0.790), (0.472, -0.845), (0.452, -0.862)],
    'collar', 96,
)
collar.data.materials.append(brass)

tip = revolve(TIP_PROFILE, 'tip', 96)
tip.data.materials.append(black)

led_glow = emission_mat('led_glow', (1.0, 0.70, 0.30, 1.0), 26.0)
build_filament(gold, glass, led_glow)
build_plasma(plasma)

if ORBIT:
    build_orbit(emission_mat('orbit_glow', (1.0, 0.86, 0.60, 1.0), 14.0))

if TILT_DEG:
    for o in bpy.context.collection.objects:
        if o.type in {'MESH', 'CURVE'} and o.name not in {'Plane'}:
            o.rotation_euler[1] = math.radians(TILT_DEG)

core = bpy.data.lights.new('core', 'POINT')
core.energy = 60.0
core.color = (1.0, 0.72, 0.34)
core.shadow_soft_size = 0.18
core_obj = bpy.data.objects.new('core', core)
core_obj.location = (0, 0, 0.30)
bpy.context.collection.objects.link(core_obj)

key = bpy.data.lights.new('key', 'AREA')
key.energy = 420.0
key.size = 5.0
key_obj = bpy.data.objects.new('key', key)
key_obj.location = (-3.2, -4.0, 2.6)
key_obj.rotation_euler = (math.radians(58), 0, math.radians(-38))
bpy.context.collection.objects.link(key_obj)

rim = bpy.data.lights.new('rim', 'AREA')
rim.energy = 260.0
rim.size = 4.0
rim_obj = bpy.data.objects.new('rim', rim)
rim_obj.location = (3.6, 3.2, 1.8)
rim_obj.rotation_euler = (math.radians(70), 0, math.radians(140))
bpy.context.collection.objects.link(rim_obj)

if MODE != 'transparent':
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -2.6))
    floor = bpy.context.object
    shade = 0.90 if MODE == 'light' else 0.035
    floor.data.materials.append(mat('floor', **{
        'Base Color': (shade, shade, shade, 1.0),
        'Roughness': 0.52,
        'Metallic': 0.0,
    }))

world = bpy.data.worlds.new('world')
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.92, 0.92, 0.93, 1.0) if MODE == 'light' else (0.02, 0.02, 0.02, 1.0)
bg.inputs['Strength'].default_value = 1.1 if MODE == 'light' else 0.25

cam_data = bpy.data.cameras.new('cam')
cam_data.lens = 90
cam = bpy.data.objects.new('cam', cam_data)
cam.location = (0, -9.0, 0.05)
cam.rotation_euler = (math.radians(90), 0, 0)
bpy.context.collection.objects.link(cam)
scene.camera = cam

scene.render.engine = 'CYCLES'
try:
    scene.cycles.device = 'GPU'
except Exception:
    pass
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 24
scene.cycles.transmission_bounces = 20
scene.cycles.transparent_max_bounces = 20
scene.render.resolution_x = RES_X
scene.render.resolution_y = RES_Y
scene.render.film_transparent = (MODE == 'transparent')
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.filepath = OUT
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Punchy'

print('Proper Electric bulb scene built. MODE=%s  ->  %s' % (MODE, OUT))
