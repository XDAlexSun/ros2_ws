#!/usr/bin/env python3
"""
Generate the MuJoCo hand (MJCF) from the URDF, so RViz and MuJoCo always show the SAME hand.

The URDF is the single source of truth: link offsets, finger lengths, joint axes, joint limits,
and which hand it is (left/right) all come from it. To change the hand, edit the URDF, then:

    python3 -m robot_sim.urdf_to_mjcf  <path/to/robot_hand.urdf>  <path/to/hand.xml>

Conventions carried over exactly:
  * URDF rpy is fixed-axis XYZ (R = Rz*Ry*Rx)  ->  MJCF eulerseq="XYZ" (capitals = extrinsic)
  * a URDF joint's origin is the child link's frame -> MJCF child <body pos= euler=>
  * a URDF joint axis is expressed in the child frame -> MJCF <joint axis=> (same)
  * URDF box size is full width, cylinder length is full length -> MJCF uses half sizes
Every revolute joint gets one position actuator (the command is a target angle in radians),
with ctrlrange equal to the URDF limit.
"""

import argparse
import sys
import xml.etree.ElementTree as ET


def _f(v):
    return f'{float(v):.6g}'


def _vec(text, default='0 0 0'):
    return [float(x) for x in (text or default).split()]


def _origin(elem):
    """(xyz, rpy) of an <origin> element; zeros when missing."""
    o = elem.find('origin') if elem is not None else None
    if o is None:
        return [0.0] * 3, [0.0] * 3
    return _vec(o.get('xyz')), _vec(o.get('rpy'))


def _color(link):
    if link.startswith('thumb'):
        return '0.90 0.55 0.35 1'      # thumb is tinted so handedness is visible at a glance
    if link == 'base_link':
        return '0.50 0.50 0.55 1'
    if link == 'palm_link':
        return '0.70 0.55 0.45 1'
    return '0.85 0.70 0.60 1'


def _geoms(link_elem, indent):
    out = []
    for i, vis in enumerate(link_elem.findall('visual')):
        shape = vis.find('geometry')[0]
        xyz, rpy = _origin(vis)
        pos = f' pos="{" ".join(map(_f, xyz))}"' if any(xyz) else ''
        eul = f' euler="{" ".join(map(_f, rpy))}"' if any(rpy) else ''
        name = f'{link_elem.get("name")}_g{i}'
        rgba = _color(link_elem.get('name'))
        if shape.tag == 'box':
            half = [float(s) / 2.0 for s in shape.get('size').split()]
            out.append(f'{indent}<geom name="{name}" type="box" size="{" ".join(map(_f, half))}"'
                       f'{pos}{eul} rgba="{rgba}"/>')
        elif shape.tag == 'cylinder':
            r, length = float(shape.get('radius')), float(shape.get('length'))
            out.append(f'{indent}<geom name="{name}" type="cylinder" size="{_f(r)} {_f(length / 2)}"'
                       f'{pos}{eul} rgba="{rgba}"/>')
        elif shape.tag == 'sphere':
            out.append(f'{indent}<geom name="{name}" type="sphere" size="{_f(shape.get("radius"))}"'
                       f'{pos}{eul} rgba="{rgba}"/>')
        else:
            raise ValueError(f'unsupported URDF geometry <{shape.tag}> on link {link_elem.get("name")}')
    return out


def convert(urdf_path):
    """Return the MJCF text for the URDF at urdf_path."""
    root = ET.parse(urdf_path).getroot()
    links = {l.get('name'): l for l in root.findall('link')}
    children = {}                      # parent link -> [joint elements]
    child_links = set()
    for j in root.findall('joint'):
        children.setdefault(j.find('parent').get('link'), []).append(j)
        child_links.add(j.find('child').get('link'))
    roots = [n for n in links if n not in child_links]
    if len(roots) != 1:
        raise ValueError(f'URDF must have exactly one root link, found {roots}')

    actuators = []

    def emit_body(link_name, joint, depth):
        ind = '  ' * depth
        lines = []
        if joint is None:
            lines.append(f'{ind}<body name="{link_name}" pos="0 0 0">')
        else:
            xyz, rpy = _origin(joint)
            pos = " ".join(map(_f, xyz))
            eul = f' euler="{" ".join(map(_f, rpy))}"' if any(rpy) else ''
            lines.append(f'{ind}<body name="{link_name}" pos="{pos}"{eul}>')
            if joint.get('type') in ('revolute', 'continuous'):
                axis = " ".join(map(_f, _vec(joint.find('axis').get('xyz'), '1 0 0')))
                lim = joint.find('limit')
                if joint.get('type') == 'revolute' and lim is not None:
                    lo, hi = float(lim.get('lower')), float(lim.get('upper'))
                    lines.append(f'{ind}  <joint name="{joint.get("name")}" axis="{axis}" '
                                 f'range="{_f(lo)} {_f(hi)}"/>')
                    actuators.append((joint.get('name'), lo, hi))
                else:
                    lines.append(f'{ind}  <joint name="{joint.get("name")}" axis="{axis}"/>')
            elif joint.get('type') != 'fixed':
                raise ValueError(f'unsupported joint type {joint.get("type")} ({joint.get("name")})')
        lines += _geoms(links[link_name], ind + '  ')
        for j in children.get(link_name, []):
            lines += emit_body(j.find('child').get('link'), j, depth + 1)
        lines.append(f'{ind}</body>')
        return lines

    body = emit_body(roots[0], None, 2)

    act = [f'    <position name="{n}_act" joint="{n}" ctrlrange="{_f(lo)} {_f(hi)}"/>'
           for n, lo, hi in actuators]

    return '\n'.join([
        '<mujoco model="robot_hand">',
        '  <!-- GENERATED from the URDF by robot_sim/urdf_to_mjcf.py. DO NOT EDIT BY HAND:',
        '       edit robot_description/urdf/robot_hand.urdf and regenerate (see the script header). -->',
        '  <compiler angle="radian" eulerseq="XYZ"/>',
        '  <option timestep="0.002" gravity="0 0 -9.81"/>',
        '  <statistic center="0 0 0.12" extent="0.35"/>',
        '',
        '  <default>',
        '    <joint type="hinge" damping="0.01" armature="0.0002"/>',
        '    <!-- contacts off: the URDF finger links have no collision geometry -->',
        '    <geom contype="0" conaffinity="0" density="1000"/>',
        '    <position kp="0.6" kv="0.02" ctrllimited="true"/>',
        '  </default>',
        '',
        '  <worldbody>',
        '    <light pos="0 -0.5 0.5" dir="0 0.7 -0.5"/>',
        '    <geom name="floor" type="plane" size="0.4 0.4 0.01" pos="0 0 -0.03" rgba="0.92 0.92 0.92 1"/>',
        *body,
        '  </worldbody>',
        '',
        '  <actuator>',
        *act,
        '  </actuator>',
        '</mujoco>',
        '',
    ])


def main(argv=None):
    p = argparse.ArgumentParser(description='Generate MuJoCo MJCF from a URDF')
    p.add_argument('urdf')
    p.add_argument('out')
    a = p.parse_args(argv)
    text = convert(a.urdf)
    with open(a.out, 'w') as f:
        f.write(text)
    print(f'wrote {a.out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
