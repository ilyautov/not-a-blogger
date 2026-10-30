# SPDX-License-Identifier: MIT
"""Optional: the same skit rendered by Blender EEVEE (soft shadows, real reflections, motion blur).

Builds a neutral room, Dude and Bot from primitives, keys head nods and mouth from timeline.json,
makes one camera per shot (a camera that exists for the whole shot keeps motion blur from smearing the cut),
then renders stills or all frames. Characters here are deliberately simple: sculpt your own or import a GLB.

  blender --background --factory-startup --python blender/render_eevee.py -- --stills 1,5 --scale 50
  blender --background --factory-startup --python blender/render_eevee.py -- --frames        # blender/frames/0001.png ...
  ffmpeg -framerate 30 -i blender/frames/%04d.png -i audio/mix.wav -c:v libx264 -pix_fmt yuv420p -shortest output/eevee.mp4

Tested with Blender 4.5 LTS API names; newer builds rename a few EEVEE settings, those are set through tryset() and skipped if absent.
EEVEE is ~50x slower than the three.js styles: keep it for hero shots and covers, iterate in three.js.
"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(HERE, 'timeline.json')))
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
opt = {}
for i, a in enumerate(argv):
    if a.startswith('--'):
        opt[a[2:]] = argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].startswith('--') else '1'
FPS, N = TL['fps'], int(TL['duration'] * TL['fps'])
scn = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
scn.render.fps = FPS; scn.frame_start = 1; scn.frame_end = N


def tryset(obj, **kw):
    for k, v in kw.items():
        try:
            setattr(obj, k, v)
        except Exception as e:  # settings move between Blender versions
            print('skip', k, e)


def mat(name, rgb, rough=.6, metal=0., coat=0., emit=0.):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if 'Coat Weight' in b.inputs: b.inputs['Coat Weight'].default_value = coat
    if emit:
        b.inputs['Emission Color'].default_value = (*rgb, 1); b.inputs['Emission Strength'].default_value = emit
    return m


def add(kind, name, loc, scale=(1, 1, 1), m=None, parent=None, **kw):
    getattr(bpy.ops.mesh, f'primitive_{kind}_add')(location=(0, 0, 0), **kw)
    o = bpy.context.active_object; o.name = name
    if parent: o.parent = parent
    o.location = loc; o.scale = scale
    if m: o.data.materials.append(m)
    if kind in ('uv_sphere', 'cylinder', 'cone'):
        for p in o.data.polygons: p.use_smooth = True
    return o


def empty(name, loc, parent=None):
    o = bpy.data.objects.new(name, None); scn.collection.objects.link(o)
    if parent: o.parent = parent
    o.location = loc; return o


# ---------- set ----------
add('plane', 'floor', (0, 0, 0), (10, 10, 1), mat('floor', (.6, .55, .48), .9))
add('plane', 'wall', (0, 3, 3), (10, 3, 1), mat('wall', (.82, .79, .74), .95)).rotation_euler = (math.radians(90), 0, 0)
add('cylinder', 'table', (0, -.1, .78), (1.1, 1.1, .04), mat('table', (.36, .25, .16), .5), vertices=48)
add('cylinder', 'table_leg', (0, -.1, .39), (.08, .08, .39), mat('leg', (.2, .22, .25), .4), vertices=24)


def character(name, x, yaw, body_rgb, head_rgb, is_bot):
    root = empty(name, (x, -.55, 0)); root.rotation_euler = (0, 0, yaw)
    body = add('uv_sphere', name + '_body', (0, 0, 1.1), (.32, .28, .5), mat(name + 'b', body_rgb, .3 if is_bot else .8, coat=1 if is_bot else 0), root)
    neck = empty(name + '_neck', (0, 0, 1.62), root)
    r = .34 if is_bot else .3
    head = add('uv_sphere', name + '_head', (0, 0, .28), (r, r, r), mat(name + 'h', head_rgb, .3 if is_bot else .55), neck)
    ink = mat(name + 'eye', (.43, .97, .91) if is_bot else (.05, .04, .04), .2, emit=4 if is_bot else 0)
    for s in (-1, 1):
        add('uv_sphere', f'{name}_eye{s}', (s * .11, -r * .9, .33), (.04, .02, .055), ink, neck)
    mouth = add('uv_sphere', name + '_mouth', (0, -r * .93, .16), (.06, .02, .015), ink if is_bot else mat(name + 'm', (.35, .1, .1), .6), neck)
    return root, neck, mouth


chars = {'dude': character('dude', -.95, math.radians(30), (.31, .49, .67), (.94, .76, .63), False),
         'bot': character('bot', .95, math.radians(-30), (.95, .96, .97), (.95, .96, .97), True)}

# ---------- animation from timeline.json: head nod + mouth from the envelope ----------
for who, (root, neck, mouth) in chars.items():
    for f in range(N):
        t = f / FPS; env = 0.
        for ln in TL['lines']:
            if ln['who'] == who and ln['start'] <= t < ln['end']:
                k = int((t - ln['start']) * FPS); env = ln['env'][min(k, len(ln['env']) - 1)]
        neck.rotation_euler = (-env * .06 + .02 * math.sin(t * .45), 0, .04 * math.sin(t * .35)); neck.keyframe_insert('rotation_euler', frame=f + 1)
        mouth.scale = (.06, .02, .015 + env * .05); mouth.keyframe_insert('scale', frame=f + 1)

# ---------- light: key / fill / rim ----------
for name, loc, energy, size in [('key', (-3, -4, 5), 900, 2.5), ('fill', (4, -5, 2), 250, 4), ('rim', (0, 3, 4), 500, 1.5)]:
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.size = size
    o = bpy.data.objects.new(name, ld); scn.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, 1.2)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()

# ---------- one camera per shot (same presets as common/core.js, roughly) ----------
def head_pos(who):
    root = chars[who][0]; return root.matrix_world @ Vector((0, 0, 1.9))


cams = {}
bpy.context.view_layer.update()
for k, sh in enumerate(TL['shots']):
    cd = bpy.data.cameras.new(f'cam{k}'); cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 24; cd.lens = 42
    cd.dof.use_dof = True; cd.dof.aperture_fstop = 2.8
    cam = bpy.data.objects.new(f'cam{k}', cd); scn.collection.objects.link(cam)
    if sh['name'] == 'wide':
        tgt = (head_pos('dude') + head_pos('bot')) / 2; d = Vector((0, -1, .25)).normalized() * 8
    else:
        who = 'bot' if sh['name'].startswith('bot') else 'dude'; tgt = head_pos(who)
        yaw = chars[who][0].rotation_euler.z; d = Vector((math.sin(yaw), -math.cos(yaw), .08)).normalized() * (2.6 if sh['name'].endswith('_tight') else 3.6)
    cam.location = tgt + d; cam.rotation_euler = (tgt - Vector((0, 0, .12)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cd.dof.focus_distance = d.length; cams[k] = cam


def shot_at(t):
    k = 0
    for i, s in enumerate(TL['shots']):
        if t >= s['start']: k = i
    return k


# ---------- EEVEE ----------
for engine in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
    try:
        scn.render.engine = engine; break
    except TypeError:
        continue
tryset(scn.eevee, taa_render_samples=int(opt.get('samples', 32)), use_shadows=True, use_raytracing=True, use_fast_gi=True)
scn.render.use_motion_blur = True
scn.render.resolution_x, scn.render.resolution_y = 1080, 1920; scn.render.resolution_percentage = int(opt.get('scale', 100))
tryset(scn.view_settings, view_transform='AgX')
w = bpy.data.worlds.new('W'); scn.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Strength'].default_value = .3
scn.render.image_settings.file_format = 'PNG'

if 'stills' in opt:
    d = os.path.join(HERE, 'stills'); os.makedirs(d, exist_ok=True)
    for t in map(float, opt['stills'].split(',')):
        f = int(t * FPS); scn.camera = cams[shot_at(t)]; scn.frame_set(f + 1)
        scn.render.filepath = os.path.join(d, f'eevee-{t:05.2f}.png'); bpy.ops.render.render(write_still=True)
elif 'frames' in opt:
    d = os.path.join(HERE, 'blender/frames'); os.makedirs(d, exist_ok=True)
    for f in range(N):
        scn.camera = cams[shot_at(f / FPS)]; scn.frame_set(f + 1)
        scn.render.filepath = os.path.join(d, f'{f + 1:04d}.png'); bpy.ops.render.render(write_still=True)
print('EEVEE DONE')
