"""Builds the looping gesture of loading a magazine: the left hand holds it, the right hand fetches a round and presses it in.

    python tools/anim/build_load_gesture.py

Needs the Arma 3 Samples (skeleton pivots and bone list), writes addons/handling/anims/load.rtm plus a JSON file next to
this script that the preview reads. Arms and hands are posed with two-bone IK from hand targets; everything else stays
in the bind pose. RTM space: Y up, the character faces -Z, its right is -X.
"""

import json
import math
import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from armaformats import read_p3d, read_rtm, write_rtm

SAMPLES = Path(os.environ.get("ARMA3_SAMPLES", r"C:\SteamLibrary\steamapps\common\Arma 3 Samples\Addons"))
BODY = SAMPLES / "Test_Character_01" / "A3_character_template.p3d"
OUTPUT = Path(__file__).resolve().parents[2] / "addons" / "handling" / "anims" / "load.rtm"
PREVIEW_DATA = Path(__file__).resolve().parent / "load_preview.json"


FRAMES = 25
PELVIS_HEIGHT = 0.912

# The magazine the left hand closes around, in the game's axes of the unit (right, forward, up): its middle, the way its
# front points, its side towards the body, up. The hand is solved against this box, see solve_left_grip.
MAG_CENTER = np.array([-0.024, 0.360, 1.264])
MAG_FRONT = np.array([0.90, 0.44, 0.0])
MAG_INWARD = np.array([0.44, -0.90, 0.0])
MAG_UP = np.array([0.0, 0.0, 1.0])
MAG_DEPTH = 0.065
MAG_THICKNESS = 0.026
MAG_HEIGHT = 0.21

# The back of the magazine lies in the palm, the knuckles this far past its far side.
KNUCKLES_PAST = 0.014

# The hand holds it this far below its middle: the top must stay free for the rounds.
HAND_BELOW_MIDDLE = 0.02

# The hand turned about the magazine's up from square on its back towards its far side, so the fingers reach its front.
GRIP_TURN = math.radians(35)

# The palm's flesh gives this much around the magazine's back, it is pressed in.
CLEARANCE = -0.009

# What a human joint does, in degrees. Fingers: the last joint follows the middle one and neighbours stay alike.
WRIST_FLEX = (-60.0, 60.0)
WRIST_DEVIATION = (-30.0, 15.0)
KNUCKLE_MAX = 85.0
MIDDLE_JOINT_MAX = 100.0
LAST_JOINT_FOLLOWS = 0.66
NEIGHBOUR_DIFFERENCE = 40.0
THUMB_BASE = (0.0, 50.0)
THUMB_OPPOSE = (-15.0, 40.0)
THUMB_MIDDLE = (0.0, 45.0)
THUMB_LAST = (0.0, 75.0)

# The thumb's hinges on the left hand in bind space, as measured on the Samples' grip pose.
THUMB_BASE_AXIS = np.array([-0.79, 0.26, -0.56])
THUMB_MIDDLE_AXIS = np.array([-0.75, 0.08, -0.66])
THUMB_LAST_AXIS = np.array([-0.67, -0.73, 0.10])

# How far the fingers close up beside each other, from the spread of the model's bind pose.
FINGERS_TOGETHER = 0.85

# The hand's real surface stops this far off the magazine.
TOUCH = 0.002

# The game's "lefthand" memory point in the hand's bind space, measured in the game. It moves with the fingers too, so
# measure it again after changing the grip, or the magazine sits beside where the hand was solved for.
LEFTHAND_POINT = [0.0385, -0.1174, -0.0416]

# What the right hand does in one cycle: phase, where its fingers pinch (from the magazine's top, or a place on the body),
# grip, and how far the left hand gives way as the round is pressed.
ABOVE = ("top", np.array([0.0, 0.0, 0.040]))
PRESS = ("top", np.array([0.0, 0.0, 0.004]))
POUCH = ("body", np.array([0.20, 0.17, 1.03]))
KEYS = [
    (0.00, ABOVE, 0.55, 0.0),
    (0.14, PRESS, 0.70, 1.0),
    (0.26, ABOVE, 0.50, 0.0),
    (0.58, POUCH, 0.25, 0.0),
    (0.70, POUCH, 0.85, 0.0),
    (1.00, ABOVE, 0.55, 0.0),
]

# The way the right hand's fingers and palm want to point there, in the game's axes; the wrist's limits have the last word.
RIGHT_AIM = {
    "top": (np.array([-0.85, 0.48, -0.20]), np.array([-0.15, 0.15, -0.97])),
    "body": (np.array([-0.30, 0.55, -0.78]), np.array([-0.85, -0.20, -0.48])),
}


def normal(vector):
    return vector / np.linalg.norm(vector)


def to_rtm(vector):
    """The unit's axes in the game (right, forward, up) to RTM space (Y up, facing -Z, its right is -X)."""
    return np.array([-vector[0], vector[2], -vector[1]])


def from_rtm(vector):
    return np.array([-vector[0], -vector[2], vector[1]])


def smooth(t):
    return t * t * (3 - 2 * t)


def sample_keys(keys, phase):
    for (a, pose_a, grip_a, give_a), (b, pose_b, grip_b, give_b) in zip(keys, keys[1:]):
        if a <= phase <= b:
            t = smooth((phase - a) / (b - a))
            pose = [pose_a[i] * (1 - t) + pose_b[i] * t for i in range(4)]
            return pose[0], normal(pose[1]), normal(pose[2]), pose[3], grip_a * (1 - t) + grip_b * t, give_a * (1 - t) + give_b * t

    raise ValueError(phase)


def frame_of(direction, hinge):
    """A rotation frame from a bone's direction and a hinge axis across it."""
    d = normal(direction)
    h = normal(hinge - d * np.dot(hinge, d))
    return np.column_stack((d, h, np.cross(d, h)))


def axis_rotation(axis, angle):
    x, y, z = normal(axis)
    c, s = math.cos(angle), math.sin(angle)
    t = 1 - c
    return np.array([
        [t * x * x + c, t * x * y - s * z, t * x * z + s * y],
        [t * x * y + s * z, t * y * y + c, t * y * z - s * x],
        [t * x * z - s * y, t * y * z + s * x, t * z * z + c],
    ])


class Skeleton:
    def __init__(self):
        pivots = read_p3d(SAMPLES / "TemplateRTM" / "ManSkeleton_Pivots.p3d")[0]
        self.pivot = {
            name.lower(): np.mean([pivots.points[i] for i in points], axis=0)
            for name, points in pivots.selections.items()
        }
        self.bones = read_rtm(SAMPLES / "Test_Anims" / "AmovPercMstpSrasWrflDnon.rtm").bones
        self.lift = np.array([0.0, PELVIS_HEIGHT, 0.0])

    def p(self, name):
        return self.pivot[name.lower()]


def solve_elbow(shoulder, wrist, upper, lower, pole):
    span = wrist - shoulder
    distance = min(np.linalg.norm(span), (upper + lower) * 0.999)
    axis = normal(span)
    along = (upper ** 2 - lower ** 2 + distance ** 2) / (2 * distance)
    height = math.sqrt(max(upper ** 2 - along ** 2, 0.0))
    side = normal(pole - axis * np.dot(pole, axis))
    return shoulder + axis * along + side * height


def hand_axes(skeleton, side):
    """The hand's axes in bind space: fingers along the middle knuckle, the side from index to pinky, palm across."""
    p = skeleton.p
    wrist_at = p(f"{side}Hand")
    fingers = normal(p(f"{side}HandMiddle1") - wrist_at)
    across = normal(p(f"{side}HandPinky1") - p(f"{side}HandIndex1"))
    # Measured on the Samples' grip pose: fingers turn about index-to-pinky on the right hand, the reverse on the left.
    sign = 1 if side == "right" else -1
    palm = normal(np.cross(across, fingers)) * sign
    # The right hand's hinges are the left's in the mirror across the body.
    mirror = np.array([1.0, -1.0, -1.0]) if side == "right" else np.ones(3)
    return {
        "fingers": fingers,
        "palm": palm,
        "curl": across * sign,
        "thumb_base": normal(THUMB_BASE_AXIS * mirror),
        "thumb_middle": normal(THUMB_MIDDLE_AXIS * mirror),
        "thumb_last": normal(THUMB_LAST_AXIS * mirror),
    }


def hand_frame(skeleton, side, fingers, palm):
    """The rotation that takes the hand from its bind pose to fingers and palm pointing as asked."""
    axes = hand_axes(skeleton, side)
    bind = np.column_stack((axes["fingers"], axes["palm"], np.cross(axes["fingers"], axes["palm"])))
    target_palm = normal(palm - fingers * np.dot(palm, fingers))
    return np.column_stack((fingers, target_palm, np.cross(fingers, target_palm))) @ bind.T


def thumb_turn(axes, angles, joint):
    """The thumb swings across the palm and turns to face the fingers at its base, then bends at its other two joints.
    angles: base, oppose, middle, last, in radians."""
    if joint == 1:
        return axis_rotation(axes["fingers"], angles[1]) @ axis_rotation(axes["thumb_base"], angles[0])

    return axis_rotation(axes["thumb_middle" if joint == 2 else "thumb_last"], angles[joint])


def wrist_angles(forearm, hand, skeleton, side):
    """Hand against forearm, degrees: flexion is towards the palm, deviation towards the thumb."""
    axes = hand_axes(skeleton, side)
    fingers = hand @ axes["fingers"]
    palm = hand @ axes["palm"]
    thumb = np.cross(fingers, palm)
    toward = hand @ normal(skeleton.p(f"{side}HandThumb1") - skeleton.p(f"{side}Hand"))

    if np.dot(thumb, toward) < 0:
        thumb = -thumb

    d = normal(forearm)
    return math.degrees(math.atan2(-np.dot(d, palm), np.dot(d, fingers))), math.degrees(math.atan2(-np.dot(d, thumb), np.dot(d, fingers)))


def over_limit(value, limits):
    return max(limits[0] - value, value - limits[1], 0.0)


def best_pole(skeleton, side, wrist, hand):
    """The elbow that leaves the wrist straightest, off the body and below the shoulder."""
    p = skeleton.p
    shoulder = p(f"{side}Arm") + skeleton.lift
    upper = np.linalg.norm(p(f"{side}ForeArm") - p(f"{side}Arm"))
    lower = np.linalg.norm(p(f"{side}Hand") - p(f"{side}ForeArm"))
    outward = np.array([1.0 if side == "left" else -1.0, 0.0, 0.0])
    down = np.array([0.0, -1.0, 0.0])
    best = None

    for angle in np.radians(np.arange(-30.0, 121.0, 5.0)):
        pole = down * math.cos(angle) + outward * math.sin(angle)
        elbow = solve_elbow(shoulder, wrist, upper, lower, pole)
        flex, deviation = wrist_angles(wrist - elbow, hand, skeleton, side)
        side_off = abs(elbow[0])
        cost = abs(flex) * 0.3 + abs(deviation) * 0.3 + over_limit(flex, WRIST_FLEX) * 5 + over_limit(deviation, WRIST_DEVIATION) * 5
        # An elbow hangs: well below the shoulder unless the wrist's limits ask for more.
        cost += max(0.22 - side_off, 0.0) * 400 + max(elbow[1] - shoulder[1] + 0.20, 0.0) * 150 + abs(angle) * 2

        if best is None or cost < best[0]:
            best = (cost, pole, flex, deviation)

    return best[1], best[2], best[3]


class MagazineBox:
    """What the hand closes around: the outline of the game's AK12, Stanag and MX magazines, placed as fnc_holdMagazine
    places them, one slab per height (mag_envelope.json). Below zero is inside."""

    def __init__(self):
        envelope = json.loads((Path(__file__).resolve().parent / "mag_envelope.json").read_text(encoding="utf-8"))
        self.z = np.array(envelope["z"])
        self.rows = np.array(envelope["rows"])
        self.step = envelope["step"]
        self.center = to_rtm(MAG_CENTER)
        self.axes = np.column_stack((to_rtm(normal(MAG_FRONT)), to_rtm(normal(MAG_INWARD)), to_rtm(MAG_UP)))

        # At the hand's height: how far its front and sides lie from the middle.
        near = np.abs(self.z + HAND_BELOW_MIDDLE) <= 0.05
        self.front = float(np.max(self.rows[near, 1]))
        self.side = float(np.max(np.abs(self.rows[near, 2:])))
        self.half = np.array([MAG_DEPTH / 2, self.side, MAG_HEIGHT / 2])

    def local(self, points):
        return (points - self.center) @ self.axes

    def distance(self, points):
        local = self.local(points)
        index = np.clip(np.round((local[..., 2] - self.z[0]) / self.step).astype(int), 0, len(self.z) - 1)
        rows = self.rows[index]
        dx = np.maximum(rows[..., 0] - local[..., 0], local[..., 0] - rows[..., 1])
        dy = np.maximum(rows[..., 2] - local[..., 1], local[..., 1] - rows[..., 3])
        dz = np.maximum(self.z[0] - self.step / 2 - local[..., 2], local[..., 2] - self.z[-1] - self.step / 2)
        outside = np.sqrt(np.maximum(dx, 0.0) ** 2 + np.maximum(dy, 0.0) ** 2 + np.maximum(dz, 0.0) ** 2)
        inside = np.minimum(np.maximum(np.maximum(dx, dy), dz), 0.0)
        return outside + inside


def hand_vertices():
    """The left hand's vertices in bind space, by the bone that holds them most."""
    male = read_p3d(BODY)[0]
    points = np.array(male.points)
    bones = ["lefthand", "lefthandring"] + [f"lefthand{f}{j}" for f in ("index", "middle", "ring", "pinky", "thumb") for j in (1, 2, 3)]
    weights = np.zeros((len(points), len(bones)))

    for name, members in male.selections.items():
        if name.lower() in bones:
            for index, value in members.items():
                weights[index, bones.index(name.lower())] = value

    best = np.argmax(weights, axis=1)
    held = np.max(weights, axis=1) > 0.4
    return {bone: points[held & (best == i)] for i, bone in enumerate(bones)}


def chain(hand, wrist_at, wrist, skeleton, bones, turns):
    """The vertices of a finger's joints, each joint turned by turns[joint] on top of its parent."""
    rotation = hand
    at = wrist + hand @ (skeleton.p(bones[0][0]) - wrist_at)
    out = []
    previous = None

    for (bone, vertices), turn in zip(bones, turns):
        pivot = skeleton.p(bone)

        if previous is not None:
            at = at + rotation @ (pivot - previous)

        rotation = rotation @ turn
        out.append(at + (vertices - pivot) @ rotation.T)
        previous = pivot

    return out


def closing_spread(skeleton, axes, finger):
    """The turn about the palm that takes a finger most of the way to lying beside the middle finger."""
    p = skeleton.p
    own = normal(p(f"leftHand{finger}2") - p(f"leftHand{finger}1"))
    middle = normal(p("leftHandMiddle2") - p("leftHandMiddle1"))
    flat = normal(own - axes["palm"] * np.dot(own, axes["palm"]))
    target = normal(middle - axes["palm"] * np.dot(middle, axes["palm"]))
    angle = math.acos(min(1.0, np.dot(flat, target)))
    sign = 1.0 if np.dot(axis_rotation(axes["palm"], angle) @ flat, target) > np.dot(axis_rotation(axes["palm"], -angle) @ flat, target) else -1.0
    return sign * angle * FINGERS_TOGETHER


def solve_left_grip(skeleton):
    """Places the hand against the box and closes every finger as far as it goes without entering it.

    The back of the magazine lies in the palm. The fingers go along its far side and around its front, the thumb along
    its near side, so the hand encloses it.
    """
    box = MagazineBox()
    front, inward, up = box.axes.T
    fingers = normal(-inward * math.cos(GRIP_TURN) + front * math.sin(GRIP_TURN))
    palm = normal(front * math.cos(GRIP_TURN) + inward * math.sin(GRIP_TURN))
    hand = hand_frame(skeleton, "left", fingers, palm)
    axes = hand_axes(skeleton, "left")
    wrist_at = skeleton.p("leftHand")
    vertices = hand_vertices()
    palm_vertices = np.vstack((vertices["lefthand"], vertices["lefthandring"]))

    # Knuckles past the far side and level with the middle; the palm just off the magazine's back.
    knuckles = np.mean([hand @ (skeleton.p(f"leftHand{f}1") - wrist_at) for f in ("Index", "Pinky")], axis=0)
    posed_palm = (palm_vertices - wrist_at) @ hand.T
    wrist = box.center - inward * (box.half[1] + KNUCKLES_PAST + np.dot(knuckles, inward)) - up * (HAND_BELOW_MIDDLE + np.dot(knuckles, up)) - front * 0.25

    # Slides up to the magazine until the palm touches it.
    for _ in range(400):
        if np.min(box.distance(wrist + front * 0.001 + posed_palm)) <= CLEARANCE:
            break

        wrist = wrist + front * 0.001

    grip = {"Spread": {}}
    limit = math.radians(NEIGHBOUR_DIFFERENCE)

    for finger, neighbour in (("Middle", None), ("Index", "Middle"), ("Ring", "Middle"), ("Pinky", "Ring")):
        grip["Spread"][finger] = closing_spread(skeleton, axes, finger)
        spread = axis_rotation(axes["palm"], grip["Spread"][finger])
        bones = [(f"leftHand{finger}{j}", vertices[f"lefthand{finger.lower()}{j}"]) for j in (1, 2, 3)]
        tip_vertex = int(np.argmax(np.linalg.norm(bones[2][1] - skeleton.p(bones[2][0]), axis=1)))
        best = None

        for a1 in np.arange(0.0, math.radians(KNUCKLE_MAX) + 0.001, 0.05):
            if neighbour and abs(a1 - grip[neighbour][0]) > limit:
                continue

            for a2 in np.arange(0.0, math.radians(MIDDLE_JOINT_MAX) + 0.001, 0.05):
                if neighbour and abs(a2 - grip[neighbour][1]) > limit:
                    continue

                a3 = a2 * LAST_JOINT_FOLLOWS
                turns = [spread @ axis_rotation(axes["curl"], a1), axis_rotation(axes["curl"], a2), axis_rotation(axes["curl"], a3)]
                parts = chain(hand, wrist_at, wrist, skeleton, bones, turns)
                distances = [float(np.min(box.distance(part))) for part in parts]

                if min(distances) < TOUCH:
                    continue

                tip = box.local(parts[2][tip_vertex])

                if tip[0] <= 0.0:
                    continue

                # Along the far side, around the front as far as it reaches, and against the magazine.
                score = distances[0] * 0.5 + distances[1] + distances[2] - 2.0 * min(tip[0], box.front + 0.006) - 2.0 * min(tip[1], 0.0)

                if best is None or score < best[0]:
                    best = (score, (a1, a2, a3), tip)

        grip[finger] = tuple(float(v) for v in best[1])
        print(f"{finger}: joints {np.round(np.degrees(best[1])).tolist()} tip in the box's axes {np.round(best[2], 3).tolist()}")

    bones = [(f"leftHandThumb{j}", vertices[f"lefthandthumb{j}"]) for j in (1, 2, 3)]
    tip_vertex = int(np.argmax(np.linalg.norm(bones[2][1] - skeleton.p(bones[2][0]), axis=1)))
    best = None

    for a0 in np.radians(np.arange(THUMB_BASE[0], THUMB_BASE[1] + 0.1, 5.0)):
        for a1 in np.radians(np.arange(THUMB_OPPOSE[0], THUMB_OPPOSE[1] + 0.1, 5.0)):
            for a2 in np.radians(np.arange(THUMB_MIDDLE[0], THUMB_MIDDLE[1] + 0.1, 5.0)):
                for a3 in np.radians(np.arange(THUMB_LAST[0], THUMB_LAST[1] + 0.1, 5.0)):
                    angles = (a0, a1, a2, a3)
                    parts = chain(hand, wrist_at, wrist, skeleton, bones, [thumb_turn(axes, angles, j) for j in (1, 2, 3)])
                    distances = [float(np.min(box.distance(part))) for part in parts]

                    if min(distances) < TOUCH:
                        continue

                    # Lying against the near side, pointing towards the front.
                    tip = box.local(parts[2][tip_vertex])
                    score = distances[2] * 2.0 + distances[1] + abs(tip[1] - (box.side + 0.008)) * 4.0 - 0.8 * min(tip[0], 0.02) + abs(tip[2] + HAND_BELOW_MIDDLE) * 0.5

                    if best is None or score < best[0]:
                        best = (score, angles, tip)

    grip["Thumb"] = tuple(float(v) for v in best[1])
    print(f"Thumb: {np.round(np.degrees(best[1])).tolist()} tip in the box's axes {np.round(best[2], 3).tolist()}")
    return wrist, hand, grip


def pose_arm(skeleton, pose, side, wrist, fingers, palm, pole, grip):
    """Writes the arm's and hand's transforms (rotation, translation) into pose. side is "left" or "right"."""
    p = skeleton.p
    name = lambda bone: f"{side}{bone}"
    lift = skeleton.lift

    shoulder_at = p(name("Arm"))
    elbow_at = p(name("ForeArm"))
    wrist_at = p(name("Hand"))
    upper = np.linalg.norm(elbow_at - shoulder_at)
    lower = np.linalg.norm(wrist_at - elbow_at)

    shoulder = shoulder_at + lift
    elbow = solve_elbow(shoulder, wrist, upper, lower, pole)

    bind_upper = elbow_at - shoulder_at
    bind_lower = wrist_at - elbow_at
    forward = np.array([0.0, 0.0, -1.0])
    bind_hinge = np.cross(normal(bind_upper), forward)
    new_hinge = np.cross(normal(elbow - shoulder), normal(wrist - elbow))

    upper_rotation = frame_of(elbow - shoulder, new_hinge) @ frame_of(bind_upper, bind_hinge).T
    lower_rotation = frame_of(wrist - elbow, new_hinge) @ frame_of(bind_lower, bind_hinge).T

    hand_rotation = hand_frame(skeleton, side, fingers, palm)

    def place(bone, rotation, at):
        pose[name(bone).lower()] = (rotation, at - rotation @ p(name(bone)))

    place("Arm", upper_rotation, shoulder)
    pose[name("ArmRoll").lower()] = pose[name("Arm").lower()]
    place("ForeArm", lower_rotation, elbow)

    # A forearm turns about itself: most of that lies in the roll bone by the wrist, some in the rest of it, so the wrist
    # itself only bends.
    relative = lower_rotation.T @ hand_rotation
    w = 0.5 * math.sqrt(max(1.0 + np.trace(relative), 1e-9))
    v = np.array([relative[2, 1] - relative[1, 2], relative[0, 2] - relative[2, 0], relative[1, 0] - relative[0, 1]]) / (4.0 * w)
    twist = 2.0 * math.atan2(np.dot(v, normal(bind_lower)), w)
    fore_rotation = lower_rotation @ axis_rotation(bind_lower, twist * 0.3)
    place("ForeArm", fore_rotation, elbow)
    roll_rotation = lower_rotation @ axis_rotation(bind_lower, twist * 0.9)
    place("ForeArmRoll", roll_rotation, elbow + (roll_rotation @ (p(name("ForeArmRoll")) - elbow_at)))
    place("Hand", hand_rotation, wrist)

    # Fingers curl about the axis across the knuckles. A number closes them evenly, a dict gives each joint its angle.
    axes = hand_axes(skeleton, side)
    hand_matrix = pose[name("Hand").lower()]

    for finger, spread in (("Index", 0.85), ("Middle", 1.0), ("Ring", 1.0), ("Pinky", 1.0)):
        parent = hand_matrix

        for joint, amount in ((1, 0.95), (2, 1.25), (3, 0.8)):
            bone = name(f"Hand{finger}{joint}")
            angle = grip[finger][joint - 1] if isinstance(grip, dict) else amount * grip * spread
            turn = axis_rotation(axes["curl"], angle)

            if joint == 1 and isinstance(grip, dict):
                turn = axis_rotation(axes["palm"], grip["Spread"][finger]) @ turn

            rotation = parent[0] @ turn
            at = parent[0] @ p(bone) + parent[1]
            pose[bone.lower()] = (rotation, at - rotation @ p(bone))
            parent = pose[bone.lower()]

    pose[name("HandRing").lower()] = hand_matrix

    parent = hand_matrix

    for joint, amount in ((1, 0.25), (2, 0.55), (3, 0.6)):
        bone = name(f"HandThumb{joint}")

        if isinstance(grip, dict):
            turn = thumb_turn(axes, grip["Thumb"], joint)
        else:
            # A pinch: the thumb across towards the fingers, its last joint bending most.
            turn = thumb_turn(axes, (0.5 * grip, 0.45 * grip, 0.3 * grip, 0.7 * grip), joint)

        rotation = parent[0] @ turn
        at = parent[0] @ p(bone) + parent[1]
        pose[bone.lower()] = (rotation, at - rotation @ p(bone))
        parent = pose[bone.lower()]

    return hand_rotation


def pinch_offset(skeleton, hand, grip):
    """From the right wrist to between the thumb's and the index finger's tips."""
    pose = {}
    p = skeleton.p
    axes = hand_axes(skeleton, "right")
    rotation = hand
    at = hand @ (p("rightHandIndex1") - p("rightHand"))
    previous = p("rightHandIndex1")

    for joint, amount in ((1, 0.95), (2, 1.25), (3, 0.8)):
        pivot = p(f"rightHandIndex{joint}")
        at = at + rotation @ (pivot - previous)
        rotation = rotation @ axis_rotation(axes["curl"], amount * grip * 0.85)
        previous = pivot

    index_tip = at + rotation @ normal(p("rightHandIndex3") - p("rightHandIndex2")) * 0.024
    rotation = hand
    at = hand @ (p("rightHandThumb1") - p("rightHand"))
    previous = p("rightHandThumb1")
    angles = (0.5 * grip, 0.45 * grip, 0.3 * grip, 0.7 * grip)

    for joint in (1, 2, 3):
        pivot = p(f"rightHandThumb{joint}")
        at = at + rotation @ (pivot - previous)
        rotation = rotation @ thumb_turn(axes, angles, joint)
        previous = pivot

    thumb_tip = at + rotation @ normal(p("rightHandThumb3") - p("rightHandThumb2")) * 0.028
    return (index_tip + thumb_tip) / 2


def right_keys(skeleton):
    """Each key of the right hand: its wrist put so the pinch is where asked, the elbow and hand within what they can do."""
    box = MagazineBox()
    p = skeleton.p
    shoulder = p("rightArm") + skeleton.lift
    upper = np.linalg.norm(p("rightForeArm") - p("rightArm"))
    lower = np.linalg.norm(p("rightHand") - p("rightForeArm"))
    keys = []

    for phase, (kind, where), grip, give in KEYS:
        if kind == "top":
            target = box.center + box.axes @ np.array([0.0, 0.0, float(box.z[-1])]) + box.axes @ where
        else:
            target = to_rtm(where)

        fingers_aim, palm_aim = RIGHT_AIM[kind]
        fingers = to_rtm(normal(fingers_aim))
        palm = to_rtm(normal(palm_aim))

        for _ in range(8):
            hand = hand_frame(skeleton, "right", fingers, palm)
            wrist = target - pinch_offset(skeleton, hand, grip)
            pole, flex, deviation = best_pole(skeleton, "right", wrist, hand)
            elbow = solve_elbow(shoulder, wrist, upper, lower, pole)
            d = normal(wrist - elbow)

            # Past a limit the hand gives way towards the forearm, keeping the pinch where it is.
            over = max(over_limit(flex, WRIST_FLEX), over_limit(deviation, WRIST_DEVIATION))

            if over <= 0.0:
                break

            fingers = normal(fingers * 0.7 + d * 0.3)
            palm = normal(palm - fingers * np.dot(palm, fingers))

        print(f"right {kind}: wrist flex {flex:.0f} deviation {deviation:.0f}, wrist {np.round(from_rtm(wrist), 3).tolist()}, elbow {np.round(from_rtm(elbow), 3).tolist()}")
        keys.append((phase, (wrist, fingers, palm, pole), grip, give))

    return keys


def build():
    skeleton = Skeleton()
    identity = (np.eye(3), skeleton.lift.copy())
    phases = [i / (FRAMES - 1) for i in range(FRAMES)]
    frames = []
    rest = {bone.lower(): identity for bone in skeleton.bones}
    left_wrist_at, left_hand_rotation, left_grip = solve_left_grip(skeleton)
    left_fingers = left_hand_rotation @ hand_axes(skeleton, "left")["fingers"]
    left_palm = left_hand_rotation @ hand_axes(skeleton, "left")["palm"]

    left_pole, left_flex, left_deviation = best_pole(skeleton, "left", left_wrist_at, left_hand_rotation)
    print(f"left: wrist flex {left_flex:.0f} deviation {left_deviation:.0f}")
    keys = right_keys(skeleton)

    for phase in phases:
        pose = dict(rest)
        wrist, fingers, palm, pole, grip, give = sample_keys(keys, phase)

        # The left hand gives a little under the press, and breathes with the cycle.
        left_wrist = left_wrist_at + np.array([0.0, -0.012 * give + 0.004 * math.sin(phase * 2 * math.pi), 0.0])
        pose_arm(skeleton, pose, "left", left_wrist, left_fingers, left_palm, left_pole, left_grip)
        pose_arm(skeleton, pose, "right", wrist, fingers, palm, pole, grip)

        frames.append({
            bone: [*rotation[:, 0], *rotation[:, 1], *rotation[:, 2], *translation]
            for bone, (rotation, translation) in pose.items()
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    write_rtm(OUTPUT, skeleton.bones, phases, frames)

    # The magazine in the left hand, for the preview, in the hand's bind space and from the wrist.
    box = MagazineBox()
    PREVIEW_DATA.write_text(json.dumps({
        "center": (left_hand_rotation.T @ (box.center - left_wrist_at)).tolist(),
        "axes": (left_hand_rotation.T @ box.axes).tolist(),
        "size": (box.half * 2).tolist(),
    }), encoding="utf-8")

    print(f"{OUTPUT.name}: {FRAMES} frames, {len(skeleton.bones)} bones")
    print("left wrist in the game's axes:", np.round(from_rtm(left_wrist_at), 3).tolist())
    check_grip(skeleton, frames)

    if LEFTHAND_POINT is not None:
        point = left_wrist_at + left_hand_rotation @ np.array(LEFTHAND_POINT)
        back = box.center - box.axes[:, 0] * (MAG_DEPTH / 2)
        print("MAG_FROM_HAND:", np.round(from_rtm(back - point), 4).tolist())


def check_grip(skeleton, frames):
    """Counts the vertices of the left hand inside the magazine, weighted as the game weights them."""
    male = read_p3d(BODY)[0]
    points = np.array(male.points)
    box = MagazineBox()

    for number in (0, len(frames) // 2):
        frame = frames[number]
        out = np.zeros_like(points)
        total = np.zeros(len(points))
        left = np.zeros(len(points), dtype=bool)

        for name, members in male.selections.items():
            matrix = frame.get(name.lower())

            if matrix is None or name.startswith("-"):
                continue

            indices = np.fromiter(members.keys(), dtype=np.int32)
            values = np.fromiter(members.values(), dtype=np.float64)
            rotation = np.array(matrix[:9]).reshape(3, 3).T
            out[indices] += (points[indices] @ rotation.T + np.array(matrix[9:])) * values[:, None]
            total[indices] += values

            if name.lower().startswith("lefthand"):
                left[indices] = True

        placed = total > 0
        out[placed] /= total[placed][:, None]
        distance = box.distance(out[left])
        print(f"frame {number}: {int(np.sum(distance < 0))} of {int(np.sum(left))} hand vertices inside the magazine, deepest {min(0.0, float(np.min(distance))) * 1000:.1f} mm, nearest {float(np.min(distance)) * 1000:.1f} mm")


if __name__ == "__main__":
    build()
