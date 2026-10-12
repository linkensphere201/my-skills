---
name: blender-orbit-review
description: Render reproducible 360-degree multi-view inspections of Blender models, posed body parts, and animation frames. Use when checking silhouettes, hands, joints, clothing or deformation from several angles before delivery.
---

# Blender Orbit Review

Use `scripts/orbit_review.py` with Blender's bundled Python. It produces eight evenly spaced azimuth views by default, a contact sheet and a JSON manifest. It does not edit or save the source Blender file.

## Workflow

1. Identify the exact Blender file, mesh, rig, action and frame. Choose full-object inspection or a weighted vertex-group region. For left/right hands inspect both separately; a left-hand result does not certify the right hand.
2. Use a new output directory. Keep the same framing and elevation for before/after comparisons. Default views are 0, 45, 90, 135, 180, 225, 270 and 315 degrees around Blender Z; 0 looks from -Y. Contact sheets read left-to-right, top-to-bottom.
3. Run the script. For animation, inspect representative contact/extreme poses and playback, not only a single still frame. A hand pose isolated from the body also needs an in-context check after application to walking.
4. Actually open the contact sheet and inspect all eight views. Open ambiguous views individually. Check silhouette, finger direction/spacing, thumb placement, collapsed joints, intersections and camera clipping. Record findings and repeat after corrections. Successful rendering is not visual acceptance or a collision certificate.
5. Deliver only after reviewing the requested views. Report remaining limitations and link the output; preserve source files and earlier comparisons.

## Invocation

```text
blender -b --python-exit-code 1 -P <skill>/scripts/orbit_review.py -- --blend <file.blend> --object <mesh> --rig <armature> --action <action> --frame 1 --output <new-directory>
```

To inspect an isolated left hand, append:

```text
--group-patterns "hand_l,thumb_*_l,index_*_l,middle_*_l,ring_*_l,pinky_*_l"
```

The region is extracted from the evaluated, posed mesh, so screenshots show skin deformation. Extraction requires topology-preserving evaluation; the script refuses mismatched vertex counts. The wrist cut is an inspection boundary, not a model defect. Use the full-body mode separately to inspect interaction with surrounding geometry.

Options: `--views 8`, `--elevation 15`, `--resolution 512`, `--margin 1.25`, `--ortho-size <meters>`, `--center x,y,z`, `--samples 16`. Default framing uses the evaluated region's bounding sphere and is fixed for the whole orbit. `--ortho-size` and `--center` allow matched comparisons. A second elevation can be run into a different directory if top/bottom detail is occluded.

No Pillow, external Python packages, UI clicks or image-generation service required. Lighting is normalized with area lights and a neutral material is applied to the review copy. This checks geometry/deformation, not textures or final lighting. Existing non-target meshes are hidden from the review render. JSON records input SHA256, pose, object, group patterns, camera coordinates and output ordering.
