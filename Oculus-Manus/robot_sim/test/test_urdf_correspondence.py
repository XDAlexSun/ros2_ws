"""
Prove the MuJoCo hand IS the URDF hand.

An independent forward-kinematics routine is written here from the URDF alone (it does not share
code with the generator). For random joint angles, every link frame must land at the same place
and orientation in MuJoCo as in the URDF.

Run with:  cd robot_sim && python3 -m pytest test
"""

import os
import xml.etree.ElementTree as ET

import mujoco
import numpy as np

from robot_sim.urdf_to_mjcf import convert

HERE = os.path.dirname(os.path.abspath(__file__))
URDF = os.path.join(HERE, '..', '..', 'robot_description', 'urdf', 'robot_hand.urdf')
MODEL = os.path.join(HERE, '..', 'models', 'hand.xml')

import pytest  # noqa: E402

pytestmark = pytest.mark.skipif(not os.path.exists(URDF), reason='URDF not next to this package')


def _rot_xyz(rpy):
    """URDF rpy: fixed-axis roll, pitch, yaw -> R = Rz(yaw) Ry(pitch) Rx(roll)."""
    r, p, y = rpy
    rx = np.array([[1, 0, 0], [0, np.cos(r), -np.sin(r)], [0, np.sin(r), np.cos(r)]])
    ry = np.array([[np.cos(p), 0, np.sin(p)], [0, 1, 0], [-np.sin(p), 0, np.cos(p)]])
    rz = np.array([[np.cos(y), -np.sin(y), 0], [np.sin(y), np.cos(y), 0], [0, 0, 1]])
    return rz @ ry @ rx


def _rodrigues(axis, angle):
    a = np.asarray(axis, float)
    a = a / np.linalg.norm(a)
    k = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + np.sin(angle) * k + (1 - np.cos(angle)) * (k @ k)


def urdf_fk(q):
    """{link: (position, rotation)} in the root link frame, straight from the URDF."""
    root = ET.parse(URDF).getroot()
    joints = root.findall('joint')
    frames = {}
    parents = {j.find('child').get('link'): j for j in joints}
    all_links = [l.get('name') for l in root.findall('link')]
    base = [n for n in all_links if n not in parents][0]
    frames[base] = (np.zeros(3), np.eye(3))

    def solve(link):
        if link in frames:
            return frames[link]
        j = parents[link]
        pp, pr = solve(j.find('parent').get('link'))
        o = j.find('origin')
        xyz = [float(v) for v in (o.get('xyz') if o is not None and o.get('xyz') else '0 0 0').split()]
        rpy = [float(v) for v in (o.get('rpy') if o is not None and o.get('rpy') else '0 0 0').split()]
        rot = pr @ _rot_xyz(rpy)
        pos = pp + pr @ np.array(xyz)
        if j.get('type') == 'revolute':
            axis = [float(v) for v in j.find('axis').get('xyz').split()]
            rot = rot @ _rodrigues(axis, q.get(j.get('name'), 0.0))
        frames[link] = (pos, rot)
        return frames[link]

    for n in all_links:
        solve(n)
    return frames


def _limits():
    root = ET.parse(URDF).getroot()
    return {j.get('name'): (float(j.find('limit').get('lower')), float(j.find('limit').get('upper')))
            for j in root.findall('joint') if j.get('type') == 'revolute'}


def _mj_frames(model, data, q):
    data.qpos[:] = 0.0
    for name, val in q.items():
        data.qpos[model.jnt_qposadr[mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, name)]] = val
    mujoco.mj_forward(model, data)
    out = {}
    for b in range(model.nbody):
        name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, b)
        out[name] = (data.xpos[b].copy(), data.xmat[b].reshape(3, 3).copy())
    return out


def test_generated_file_is_up_to_date():
    """models/hand.xml must be exactly what the generator makes from the current URDF."""
    assert open(MODEL).read() == convert(URDF), (
        'URDF changed but hand.xml was not regenerated. Run:\n'
        '  python3 -m robot_sim.urdf_to_mjcf ../robot_description/urdf/robot_hand.urdf models/hand.xml')


def test_every_link_matches_urdf_forward_kinematics():
    model = mujoco.MjModel.from_xml_path(MODEL)
    data = mujoco.MjData(model)
    limits = _limits()
    rng = np.random.default_rng(1)
    poses = [{}] + [{n: rng.uniform(lo, hi) for n, (lo, hi) in limits.items()} for _ in range(25)]
    for q in poses:
        ref, got = urdf_fk(q), _mj_frames(model, data, q)
        for link, (p, r) in ref.items():
            assert np.allclose(got[link][0], p, atol=1e-9), f'position of {link} differs at {q}'
            assert np.allclose(got[link][1], r, atol=1e-9), f'orientation of {link} differs at {q}'


def test_it_is_a_right_hand():
    """
    Right-hand rule: (thumb side) x (finger direction) must equal the palm normal, where the palm
    normal is the direction the fingertips move when the fingers curl.
    """
    model = mujoco.MjModel.from_xml_path(MODEL)
    data = mujoco.MjData(model)
    f0 = _mj_frames(model, data, {})
    f1 = _mj_frames(model, data, {'middle_mcp': 0.3})

    palm = f0['palm_link'][0]
    fingers = f0['middle_proximal'][0] - palm                  # points along the fingers
    fingers /= np.linalg.norm(fingers)

    thumb = f0['thumb_proximal'][0] - f0['middle_proximal'][0]
    thumb -= np.dot(thumb, fingers) * fingers                  # sideways offset only
    thumb /= np.linalg.norm(thumb)

    tip0, tip1 = f0['middle_distal'][0], f1['middle_distal'][0]
    curl = tip1 - tip0
    curl -= np.dot(curl, fingers) * fingers
    curl /= np.linalg.norm(curl)

    handedness = np.dot(np.cross(thumb, fingers), curl)
    assert handedness > 0.5, f'this is a LEFT hand (handedness={handedness:.2f})'
