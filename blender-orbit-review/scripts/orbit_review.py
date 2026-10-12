"""Reproducible Blender orbit review; run via blender -b -P SCRIPT -- ARGS."""
import argparse
import array
import fnmatch
import hashlib
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

p=argparse.ArgumentParser()
p.add_argument('--blend',required=True);p.add_argument('--object',required=True)
p.add_argument('--rig');p.add_argument('--action');p.add_argument('--frame',type=float,default=1)
p.add_argument('--output',required=True);p.add_argument('--group-patterns',default='')
p.add_argument('--views',type=int,default=8);p.add_argument('--elevation',type=float,default=15)
p.add_argument('--resolution',type=int,default=512);p.add_argument('--margin',type=float,default=1.25)
p.add_argument('--ortho-size',type=float);p.add_argument('--center');p.add_argument('--samples',type=int,default=16)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
assert 4<=a.views<=36 and 128<=a.resolution<=2048 and a.margin>=1
source=Path(a.blend).resolve();out=Path(a.output).resolve()
assert out!=source.parent, 'Use a dedicated review directory'
if out.exists() and any(out.iterdir()):raise RuntimeError('Output must be empty; use a new review directory')
out.mkdir(parents=True,exist_ok=True)
digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene;obj=bpy.data.objects[a.object]
assert obj.type=='MESH'
if a.action:
    assert a.rig, '--action requires --rig'
    rig=bpy.data.objects[a.rig];rig.animation_data_create()
    for t in rig.animation_data.nla_tracks:t.mute=True
    rig.animation_data.action=bpy.data.actions[a.action]
    if rig.animation_data.action.slots:rig.animation_data.action_slot=rig.animation_data.action.slots[0]
scene.frame_set(math.floor(a.frame),subframe=a.frame-math.floor(a.frame))
bpy.context.view_layer.update()
evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
mesh=evaluated.to_mesh()
points=[obj.matrix_world@v.co for v in mesh.vertices]
patterns=[s for s in a.group_patterns.split(',') if s]
if patterns:
    assert len(mesh.vertices)==len(obj.data.vertices), 'Region mode needs topology-preserving evaluated mesh'
    group_ids={g.index for g in obj.vertex_groups if any(fnmatch.fnmatchcase(g.name,s) for s in patterns)}
    if not group_ids:raise RuntimeError('No vertex groups match region')
    indices={v.index for v in obj.data.vertices if sum(g.weight for g in v.groups if g.group in group_ids)>.5}
    faces=[tuple(poly.vertices) for poly in mesh.polygons if all(i in indices for i in poly.vertices)]
else:
    faces=[tuple(poly.vertices) for poly in mesh.polygons]
used=sorted({i for face in faces for i in face})
assert used, 'Empty review region'
remap={old:i for i,old in enumerate(used)}
region=bpy.data.meshes.new('OrbitReviewGeometry')
region.from_pydata([points[i] for i in used],[],[tuple(remap[i] for i in f) for f in faces]);region.update()
target=bpy.data.objects.new('OrbitReviewTarget',region);scene.collection.objects.link(target)
material=bpy.data.materials.new('OrbitReviewNeutral');material.diffuse_color=(.65,.65,.65,1)
material.use_nodes=True;material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.65,.65,.65,1)
material.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.75
region.materials.append(material)
for polygon in region.polygons:polygon.use_smooth=True
evaluated.to_mesh_clear()
for other in scene.objects:
    if other.type in ['MESH','CURVE','FONT','LIGHT'] and other!=target:other.hide_render=True
coords=[points[i] for i in used]
center=Vector(tuple(map(float,a.center.split(',')))) if a.center else Vector(tuple((min(v[k] for v in coords)+max(v[k] for v in coords))/2 for k in range(3)))
radius=max((v-center).length for v in coords)
size=a.ortho_size or 2*radius*a.margin
camdata=bpy.data.cameras.new('OrbitReviewCamera');cam=bpy.data.objects.new('OrbitReviewCamera',camdata);scene.collection.objects.link(cam)
scene.camera=cam;camdata.type='ORTHO';camdata.ortho_scale=size;camdata.clip_start=.001;camdata.clip_end=max(100,radius*30)
for i,offset in enumerate([(3,-4,4),(-4,-1,2),(1,4,3)]):
    ld=bpy.data.lights.new('OrbitReviewLight'+str(i),'AREA');lo=bpy.data.objects.new(ld.name,ld);scene.collection.objects.link(lo)
    lo.location=center+Vector(offset)*max(radius,.1);lo.rotation_euler=(center-lo.location).to_track_quat('-Z','Y').to_euler()
    ld.energy=250*max(radius,.1)**2;ld.shape='DISK';ld.size=max(radius,.1)*3
scene.world=bpy.data.worlds.new('OrbitReviewWorld');scene.world.color=(.16,.16,.16)
scene.render.engine='CYCLES';scene.cycles.samples=a.samples
scene.render.resolution_x=a.resolution;scene.render.resolution_y=a.resolution;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
views=[];cols=4;rows=math.ceil(a.views/cols);width=cols*a.resolution;height=rows*a.resolution
pixels=array.array('f',[.08,.08,.08,1.])*(width*height)
for i in range(a.views):
    az=math.tau*i/a.views;el=math.radians(a.elevation)
    offset=Vector((math.sin(az)*math.cos(el),-math.cos(az)*math.cos(el),math.sin(el)))*max(radius*5,1)
    cam.location=center+offset;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    path=out/f'view-{i:02d}-{round(math.degrees(az)):03d}.png';scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    im=bpy.data.images.load(str(path),check_existing=False);buf=array.array('f',[0.])*(a.resolution*a.resolution*4);im.pixels.foreach_get(buf)
    x=(i%cols)*a.resolution;y=(rows-1-i//cols)*a.resolution
    for row in range(a.resolution):
        dst=((y+row)*width+x)*4;start=row*a.resolution*4
        pixels[dst:dst+a.resolution*4]=buf[start:start+a.resolution*4]
    views.append({'index':i,'azimuth_degrees':math.degrees(az),'elevation_degrees':a.elevation,'camera':list(cam.location),'file':path.name})
sheet=bpy.data.images.new('OrbitContactSheet',width=width,height=height,alpha=True)
sheet.pixels.foreach_set(pixels);sheet.filepath_raw=str(out/'contact-sheet.png');sheet.file_format='PNG';sheet.save()
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'manifest.json').write_text(json.dumps({'source':str(source),'sha256':digest,'object':a.object,'rig':a.rig,'action':a.action,'frame':a.frame,
    'group_patterns':patterns,'center':list(center),'ortho_size':size,'views':views,'contact_sheet_order':'left to right, top to bottom'},indent=2),encoding='utf8')
print('ORBIT_REVIEW_OK',out,flush=True)
