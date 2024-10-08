"""Put Blocks in Bowl Task."""

import numpy as np
from cliport.tasks.task import Task
from cliport.utils import utils

import random
import pybullet as p

class PutBlockInBowlUnseenColors(Task):
    """Put Blocks in Bowl base class and task."""

    def __init__(self):
        super().__init__()
        self.max_steps = 10
        self.pos_eps = 0.05
        self.lang_template = "put the {pick} blocks in a {place} bowl"
        self.task_completed_desc = "done placing blocks in bowls."


    def reset(self, env):
        super().reset(env)
        n_bowls = np.random.randint(1, 4)
        n_blocks = np.random.randint(1, n_bowls + 1)

        all_color_names = self.get_colors()
        selected_color_names = random.sample(all_color_names, 2)
        colors = [utils.COLORS[cn] for cn in selected_color_names]

        # Add bowls.
        bowl_size = (0.12, 0.12, 0)
        bowl_urdf = 'bowl/bowl.urdf'
        bowl_poses = []
        for _ in range(n_bowls):
            bowl_pose = self.get_random_pose(env, bowl_size)
            bowl_id = env.add_object(bowl_urdf, bowl_pose, 'fixed')
            p.changeVisualShape(bowl_id, -1, rgbaColor=colors[1] + [1])
            bowl_poses.append(bowl_pose)

        # Add blocks.
        blocks = []
        block_size = (0.04, 0.04, 0.04)
        block_urdf = 'stacking/block.urdf'
        for _ in range(n_blocks):
            block_pose = self.get_random_pose(env, block_size)
            block_id = env.add_object(block_urdf, block_pose)
            p.changeVisualShape(block_id, -1, rgbaColor=colors[0] + [1])
            blocks.append((block_id, (0, None)))

        # Goal: put each block in a different bowl.
        self.goals.append((blocks, np.ones((len(blocks), len(bowl_poses))),
                           bowl_poses, False, True, 'pose', None, 1))
        self.lang_goals.append(self.lang_template.format(pick=selected_color_names[0],
                                                         place=selected_color_names[1]))

        # Only one mistake allowed.
        self.max_steps = len(blocks) + 1

        # Colors of distractor objects.
        distractor_bowl_colors = [utils.COLORS[c] for c in utils.COLORS if c not in selected_color_names]
        distractor_block_colors = [utils.COLORS[c] for c in utils.COLORS if c not in selected_color_names]

        # Add distractors.
        n_distractors = 0
        max_distractors = 6
        while n_distractors < max_distractors:
            is_block = np.random.rand() > 0.5
            urdf = block_urdf if is_block else bowl_urdf
            size = block_size if is_block else bowl_size
            colors = distractor_block_colors if is_block else distractor_bowl_colors
            pose = self.get_random_pose(env, size)
            if not pose:
                continue
            obj_id = env.add_object(urdf, pose)
            color = colors[n_distractors % len(colors)]
            if not obj_id:
                continue
            p.changeVisualShape(obj_id, -1, rgbaColor=color + [1])
            n_distractors += 1

    def get_colors(self):
        return utils.TRAIN_COLORS if self.mode == 'train' else utils.EVAL_COLORS


class PutBlockInBowlSeenColors(PutBlockInBowlUnseenColors):
    def __init__(self):
        super().__init__()

    def get_colors(self):
        return utils.TRAIN_COLORS


class PutBlockInBowlFull(PutBlockInBowlUnseenColors):
    def __init__(self):
        super().__init__()

    def get_colors(self):
        all_colors = list(set(utils.TRAIN_COLORS) | set(utils.EVAL_COLORS))
        return all_colors


class PutBlockInMismatchingBowl(Task):
    """Put the blocks in the bowls with mismatched colors base class and task"""

    def __init__(self):
        super().__init__()
        self.max_steps = 10
        self.pos_eps = 0.05
        self.lang_template = "put the blocks in the bowls with mismatched colors."
        self.task_completed_desc = "done placing blocks in bowls."

    def reset(self, env):
        super().reset(env)
        n_bowls = np.random.randint(5, 8)
        n_blocks = np.random.randint(5, n_bowls + 1)

        all_color_names = self.get_colors()
        selected_color_names = random.sample(all_color_names, n_bowls)

        colors = [utils.COLORS[cn] for cn in selected_color_names]

        self.place_obj_names, self.pick_obj_names = [], []
        pick_obj_names, place_obj_names = [], []
        self.task_name = "put-block-in-mismatching-bowl"

        # Add bowls.
        bowl_size = (0.12, 0.12, 0)
        bowl_urdf = 'bowl/bowl.urdf'
        bowl_poses = []
        for i, _ in enumerate(range(n_bowls)):
            bowl_pose = self.get_random_pose(env, bowl_size)
            bowl_id = env.add_object(bowl_urdf, bowl_pose, 'fixed')
            p.changeVisualShape(bowl_id, -1, rgbaColor=colors[i] + [1])
            bowl_poses.append(bowl_pose)
            place_obj_names.append(f"{selected_color_names[i]} bowl")
        self.place_obj_names.append(place_obj_names)

        # Add blocks.
        blocks = []
        block_size = (0.04, 0.04, 0.04)
        block_urdf = 'stacking/block.urdf'
        for i, _ in enumerate(range(n_blocks)):
            block_pose = self.get_random_pose(env, block_size)
            block_id = env.add_object(block_urdf, block_pose)
            p.changeVisualShape(block_id, -1, rgbaColor=colors[i] + [1])
            blocks.append((block_id, (0, None)))
            pick_obj_names.append(f"{selected_color_names[i]} block")
        self.pick_obj_names.append(pick_obj_names)

        # Goal: put each block in a bowl with mismatching color.
        self.goals.append((blocks, 1 - np.eye(len(blocks)), bowl_poses, False, True, 'pose', None, 1))
        self.lang_goals.append(self.lang_template)

        # Only one mistake allowed.
        self.max_steps = len(blocks) + 2

        # Colors of distractor objects.
        # distractor_bowl_colors = [utils.COLORS[c] for c in utils.COLORS if c not in selected_color_names]
        # distractor_block_colors = [utils.COLORS[c] for c in utils.COLORS if c not in selected_color_names]
        distractor_color_name = [c for c in utils.COLORS if c not in selected_color_names]
        distractor_colors = [utils.COLORS[c] for c in distractor_color_name]

        # Add distractors.
        n_distractors = 0
        max_distractors = 6
        distractor_block = []
        while n_distractors < max_distractors and distractor_colors:
            is_block = False
            urdf = block_urdf if is_block else bowl_urdf
            size = block_size if is_block else bowl_size
            colors = distractor_colors
            pose = self.get_random_pose(env, size)
            if not pose:
                continue
            obj_id = env.add_object(urdf, pose)
            color = colors[n_distractors % len(colors)]
            color_name = distractor_color_name[n_distractors % len(colors)]
            distractor_colors.remove(color)
            distractor_color_name.remove(color_name)
            if not obj_id:
                continue
            p.changeVisualShape(obj_id, -1, rgbaColor=color + [1])
            distractor_block.append(color_name)
            n_distractors += 1

        self.scene_description = f"On the table, there are {n_blocks + len(distractor_block)} blocks. " \
                                 f"Their colors are {selected_color_names[:n_blocks] + distractor_block}. " \
                                 f"There are {n_bowls} bowls. " \
                                 f"Their colors are {selected_color_names[:n_bowls]}."

    def get_colors(self):
        return utils.TRAIN_COLORS if self.mode == 'train' else utils.EVAL_COLORS


class PutBlockInMatchingBowl(Task):
    """Put Block in Matching Bowl base class and task."""

    def __init__(self):
        super().__init__()
        self.max_steps = 10
        self.pos_eps = 0.05
        self.final_goal="put blocks in matching bowls"
        self.task_name="put-blocks-in-matching-bowls "
        self.lang_template = "put the {pick_color} block in the {place_color} bowl."
        self.task_completed_desc = "done PutBlockInMatchingBowl."
        self.question_template = "Did the robot successfully execute the action 'put the {pick_color} block in the {place_color} bowl', and did any anomaly happen?"
        self.answer_template = "The action succeeded, and "
        self.seed = 0

    def reset(self, env):
        super().reset(env)

        trashcan_pose = ((0.35, random.choice([-0.4, 0.4]), 0.05), (0.0, 0.0, 0.12, 0.1))
        container_template = 'trash_can/trashcan.urdf'
        env.add_object(container_template, trashcan_pose, 'fixed')

        n_bowls = np.random.randint(3, 4)
        n_blocks = np.random.randint(3, n_bowls + 1)

        all_color_names = self.get_colors()
        selected_color_names = random.sample(all_color_names, n_bowls)

        colors = [utils.COLORS[cn] for cn in selected_color_names]
        self.block_info=[]
        self.bowl_info=[]
        self.gt_step=n_bowls

        # Add bowls.
        bowl_size = (0.12, 0.12, 0)
        bowl_urdf = 'bowl/bowl.urdf'
        bowl_poses = []
        for i in range(n_bowls):
            bowl_pose = self.get_random_pose(env, bowl_size)
            bowl_id = env.add_object(bowl_urdf, bowl_pose, 'fixed')
            p.changeVisualShape(bowl_id, -1, rgbaColor=colors[i] + [1])
            bowl_poses.append(bowl_pose)
            self.bowl_info.append([bowl_id,selected_color_names[i],bowl_pose])
        # Add blocks.
        blocks = []
        block_size = (0.04, 0.04, 0.04)
        block_urdf = 'stacking/block.urdf'
        for i in range(n_blocks):
            block_pose = self.get_random_pose(env, block_size)
            block_id = env.add_object(block_urdf, block_pose)
            p.changeVisualShape(block_id, -1, rgbaColor=colors[i] + [1])
            blocks.append((block_id, (0, None)))
            self.block_info.append([block_id,selected_color_names[i],block_pose])

        # Goal: put each block in a different bowl.
        self.goals.append((blocks, np.eye(len(blocks)), bowl_poses, False, True, 'pose', None, 1))

        # Only one mistake allowed.
        self.max_steps = len(blocks) + 2

        # Colors of distractor objects.
        # distractor_bowl_colors = [utils.COLORS[c] for c in utils.COLORS if c not in selected_color_names]
        # distractor_block_colors = [utils.COLORS[c] for c in utils.COLORS if c not in selected_color_names]
        distractor_color_names = [c for c in utils.COLORS if c not in selected_color_names]
        distractor_colors = [utils.COLORS[c] for c in distractor_color_names]

        # Add distractors.
        n_distractors = 0
        max_distractors = 6
        distractor_block = []
        distractor_bowl = []
        while n_distractors < max_distractors and distractor_colors:
            is_block = np.random.rand() > 0.5
            urdf = block_urdf if is_block else bowl_urdf
            size = block_size if is_block else bowl_size
            colors = distractor_colors
            pose = self.get_random_pose(env, size)
            if None in pose:
                continue

            color_name = distractor_color_names[n_distractors % len(colors)]
            color = colors[n_distractors % len(colors)]
            if is_block:
                obj_id = env.add_object(urdf, pose)
                distractor_block.append(color_name)
                self.block_info.append([obj_id,color_name,pose])
            else:
                obj_id = env.add_object(urdf, pose,'fixed')
                distractor_bowl.append(color_name)
                self.bowl_info.append([obj_id,color_name,pose])
            distractor_colors.remove(color)
            distractor_color_names.remove(color_name)
            if not obj_id:
                continue
            p.changeVisualShape(obj_id, -1, rgbaColor=color + [1])
            n_distractors += 1
        block_list = selected_color_names[:n_blocks] + distractor_block
        np.random.shuffle(block_list)
        bowl_list = selected_color_names[:n_bowls] + distractor_bowl
        np.random.shuffle(bowl_list)
        self.scene_description = f"On the table, there are {n_blocks + len(distractor_block)} blocks. " \
                                 f"Their colors are {', '.join(block_list)}. " \
                                 f"There are {n_bowls + len(distractor_bowl)} bowls. " \
                                 f"Their colors are {', '.join(bowl_list)}."
        self.lang_goals.append(self.lang_template)
        self.question_list.append(self.question_template)
        self.answer_list.append(self.answer_template)
        self.build_initial_scene_description()

        return True

    def build_initial_scene_description(self):
        info = "In the initial state, there are "
        for i in range(len(self.block_info) - 1):
            info += self.block_info[i][1] + ', '
        info += "and " + self.block_info[-1][1]  + " blocks; there are "
        for i in range(len(self.bowl_info) - 1):
            info += self.bowl_info[i][1] + ', '
        info += "and " + self.bowl_info[-1][1] + " bowls; and a trash can."

        self.initial_state = info


    def get_colors(self):
            return utils.ALL_COLORS

class PutAllBlockInABowl(Task):
    """Put all the blocks in a bowl base class and task"""

    def __init__(self):
        super().__init__()
        self.max_steps = 10
        self.pos_eps = 0.05
        self.lang_template = "put all the blocks in the {color} bowl"
        self.task_completed_desc = "done placing blocks in bowls."

    def reset(self, env):
        super().reset(env)
        # n_bowls = np.random.randint(1, 4)
        # n_blocks = np.random.randint(1, 2)
        n_bowls = 5
        n_blocks = 2

        all_color_names = self.get_colors()
        bowl_color = random.sample(all_color_names, n_bowls)
        block_color = random.sample(all_color_names, n_blocks)
        bowl_color_ = [utils.COLORS[cn] for cn in bowl_color]
        block_color_ = [utils.COLORS[cn] for cn in block_color]

        # Add bowls.
        bowl_size = (0.12, 0.12, 0)
        bowl_urdf = 'bowl/bowl.urdf'
        bowl_poses = []
        for i in range(n_bowls):
            bowl_pose = self.get_random_pose(env, bowl_size)
            bowl_id = env.add_object(bowl_urdf, bowl_pose, 'fixed')
            p.changeVisualShape(bowl_id, -1, rgbaColor=bowl_color_[i] + [1])
            bowl_poses.append(bowl_pose)

        # Add blocks.
        blocks = []
        block_size = (0.04, 0.04, 0.04)
        block_urdf = 'stacking/block.urdf'
        for i in range(n_blocks):
            block_pose = self.get_random_pose(env, block_size)
            block_id = env.add_object(block_urdf, block_pose)
            p.changeVisualShape(block_id, -1, rgbaColor=block_color_[i] + [1])
            blocks.append((block_id, (0, None)))

        self.scene_description = f"On the table, there are {n_blocks} blocks. " \
                                 f"Their colors are {block_color}. " \
                                 f"There are {n_bowls} bowls. " \
                                 f"The colors of bowls are {bowl_color}."

        # Goal: put all the blocks in the bowl of the first color.
        matches = np.zeros((len(blocks), len(bowl_poses)))
        matches[:, 0] = 1
        self.goals.append((blocks, matches, bowl_poses, True, True, 'pose', None, 1))
        self.lang_goals.append(self.lang_template.format(color=bowl_color[0]))

        # Only one mistake allowed.
        self.max_steps = len(blocks) + 1

        # Colors of distractor objects.
        # distractor_bowl_colors = [utils.COLORS[c] for c in utils.COLORS if c not in selected_color_names]
        # distractor_block_colors = [utils.COLORS[c] for c in utils.COLORS if c not in selected_color_names]
        distractor_colors = [utils.COLORS[c] for c in utils.COLORS if c not in (bowl_color + block_color)]

        # Add distractors.
        n_distractors = 0
        max_distractors = 6
        while n_distractors < max_distractors and distractor_colors:
            is_block = False
            urdf = block_urdf if is_block else bowl_urdf
            size = block_size if is_block else bowl_size
            colors = distractor_colors
            pose = self.get_random_pose(env, size)
            if not pose:
                continue
            obj_id = env.add_object(urdf, pose)
            color = colors[n_distractors % len(colors)]
            distractor_colors.remove(color)
            if not obj_id:
                continue
            p.changeVisualShape(obj_id, -1, rgbaColor=color + [1])
            n_distractors += 1

    def get_colors(self):
        return utils.TRAIN_COLORS if self.mode == 'train' else utils.EVAL_COLORS


class PutAllBlockInAZone(Task):
    """Put all the blocks in the [x zone] base class and task. """

    def __init__(self):
        super().__init__()
        self.max_steps = 10
        self.pos_eps = 0.05
        self.lang_template = "put all the blocks in the {color} zone"
        self.task_completed_desc = "done placing blocks in the zone."

    def reset(self, env):
        super().reset(env)
        n_blocks = random.randint(1, 3)

        all_color_names = self.get_colors()
        selected_color_names = random.sample(all_color_names, n_blocks)
        colors = [utils.COLORS[cn] for cn in selected_color_names]

        zone_selected_colors = [c for c in all_color_names if c not in selected_color_names]
        zone_color_ = random.sample(zone_selected_colors, 1)[0]
        zone_color = utils.COLORS[zone_color_]
        zone_size = (0.15, 0.15, 0)
        # all_corner_names = ['bottom right corner', 'bottom side', 'bottom left corner']
        # all_corner_target_pos = [(0.65, 0.35, 0), (0.5, 0.25, 0), (0.35, 0.35, 0)]
        # all_corner_size = [(0.2, 0.3, 0), (0.5, 0.3, 0), (0.2, 0.3, 0)]
        # corner_idx = random.sample(range(len(all_corner_names)), 1)[0]

        # Add blocks.
        blocks = []
        block_pts = {}
        block_size = (0.04, 0.04, 0.04)
        block_urdf = 'stacking/block.urdf'
        for i in range(n_blocks):
            block_pose = self.get_random_pose(env, block_size)
            block_id = env.add_object(block_urdf, block_pose)
            p.changeVisualShape(block_id, -1, rgbaColor=colors[i] + [1])
            block_pts[block_id] = self.get_box_object_points(block_id)
            blocks.append((block_id, (0, None)))

        self.scene_description = f"On the table, there are {n_blocks} blocks. Their colors are {selected_color_names}. " \
                                 f"There are a zone and its color is {zone_color_}. "

        def get_certain_pose(pos):
            theta = np.random.rand() * 2 * np.pi
            rot = utils.eulerXYZ_to_quatXYZW((0, 0, theta))
            return pos, rot

        # Add zone
        # zone_size = all_corner_size[corner_idx]
        # zone_pose = get_certain_pose(all_corner_target_pos[corner_idx])
        zone_target = zone_pose = self.get_random_pose(env, zone_size)
        zone_obj_id = env.add_object('zone/zone.urdf', zone_pose, 'fixed')
        p.changeVisualShape(zone_obj_id, -1, rgbaColor=zone_color + [1])

        # Goal: put each block in the corner.
        self.goals.append((blocks, np.ones((n_blocks, 1)), [zone_target],
                           True, False, 'zone',
                           (block_pts, [(zone_target, zone_size)]), 1))
        self.lang_goals.append(self.lang_template.format(color=zone_color_))

        # Only one mistake allowed.
        self.max_steps = len(blocks) + 1

    def get_colors(self):
        return utils.TRAIN_COLORS if self.mode == 'train' else utils.EVAL_COLORS


class PutAllBlockOnCorner(Task):
    """Put all the blocks on the [x corner/side] base class and task.
    corner/side: bottom right corner, bottom side, bottom left corner"""

    # TODO: how to define corner?
    def __init__(self):
        super().__init__()
        self.max_steps = 10
        self.pos_eps = 0.05
        self.lang_template = "put all the blocks on the {corner}"
        self.task_completed_desc = "done placing blocks on the corner."

    def reset(self, env):
        super().reset(env)
        n_blocks = np.random.randint(1, 5)

        all_color_names = self.get_colors()
        selected_color_names = random.sample(all_color_names, n_blocks)
        colors = [utils.COLORS[cn] for cn in selected_color_names]

        corner_selected_colors = [c for c in all_color_names if c not in selected_color_names]
        corner_colors = [utils.COLORS[cn] for cn in corner_selected_colors]
        all_corner_names = ['bottom right corner', 'bottom side', 'bottom left corner']
        all_corner_target_pos = [(0.65, 0.35, 0), (0.5, 0.25, 0), (0.35, 0.35, 0)]
        all_corner_size = [(0.2, 0.3, 0), (0.5, 0.3, 0), (0.2, 0.3, 0)]
        corner_idx = random.sample(range(len(all_corner_names)), 1)[0]

        # Add blocks.
        blocks = []
        block_pts = {}
        block_size = (0.04, 0.04, 0.04)
        block_urdf = 'stacking/block.urdf'
        for i in range(n_blocks):
            block_pose = self.get_random_pose(env, block_size)
            block_id = env.add_object(block_urdf, block_pose)
            p.changeVisualShape(block_id, -1, rgbaColor=colors[i] + [1])
            block_pts[block_id] = self.get_box_object_points(block_id)
            blocks.append((block_id, (0, None)))

        def get_certain_pose(pos):
            theta = np.random.rand() * 2 * np.pi
            rot = utils.eulerXYZ_to_quatXYZW((0, 0, theta))
            return pos, rot

        zone_size = all_corner_size[corner_idx]
        # zone_pose = get_certain_pose(all_corner_target_pos[corner_idx])
        zone_pose = self.get_random_pose(env, zone_size)
        zone_obj_id = env.add_object('zone/zone.urdf', zone_pose, 'fixed')
        zone_color = random.sample(corner_colors, 1)
        zone_target = zone_pose
        p.changeVisualShape(zone_obj_id, -1, rgbaColor=zone_color + [1])

        # Goal: put each block in the corner.
        self.goals.append((blocks, np.ones((n_blocks, 1)), [zone_target],
                           True, False, 'zone',
                           (block_pts, [(zone_target, zone_size)]), 1))
        self.lang_goals.append(self.lang_template.format(corner=all_corner_names[corner_idx]))

        # Only one mistake allowed.
        self.max_steps = len(blocks) + 1

    def get_colors(self):
        return utils.TRAIN_COLORS if self.mode == 'train' else utils.EVAL_COLORS


class PickAndPlace(Task):
    """Pick up the [block1] and place it on the [block2/bowl/zone]."""

    def __init__(self):
        super().__init__()
        self.max_steps = 3
        self.pos_eps = 0.05
        self.lang_template = "pick up the {pick_color} block and place it on the {place_color} {place}"
        self.task_completed_desc = "done placing blocks."

    def reset(self, env):
        super().reset(env)
        target_idx = random.randint(0, 2)
        # target_idx = 1
        target_objs = ["block", "bowl", "zone"]
        all_color_names = self.get_colors()

        n_blocks = random.randint(2, 4)
        n_zones = random.randint(1, 3)
        n_bowls = random.randint(2, 4)
        # n_blocks = 4
        # n_zones = 3
        # n_bowls = 4

        block_colors = random.sample(all_color_names, n_blocks)
        bowl_colors = random.sample(all_color_names, n_bowls)
        zone_colors = random.sample(all_color_names, n_zones)
        block_util_colors = [utils.COLORS[cn] for cn in block_colors]
        bowl_util_colors = [utils.COLORS[cn] for cn in bowl_colors]
        zone_util_colors = [utils.COLORS[cn] for cn in zone_colors]

        self.scene_description = f"On the table, there are {n_blocks} blocks. Their colors are {block_colors}. " \
                                 f"There are {n_zones} zones. Their colors are {zone_colors}. " \
                                 f"There are {n_bowls} bowls. Their colors are {bowl_colors}. "

        # Add bowls.
        bowl_size = (0.12, 0.12, 0)
        bowl_urdf = 'bowl/bowl.urdf'
        bowl_poses = []
        for i in range(n_bowls):
            bowl_pose = self.get_random_pose(env, bowl_size)
            bowl_id = env.add_object(bowl_urdf, bowl_pose, 'fixed')
            p.changeVisualShape(bowl_id, -1, rgbaColor=bowl_util_colors[i] + [1])
            bowl_poses.append(bowl_pose)

        # Add blocks.
        blocks = []
        block_pts = {}
        block_size = (0.04, 0.04, 0.04)
        block_urdf = 'stacking/block.urdf'
        for i in range(n_blocks):
            block_pose = self.get_random_pose(env, block_size)
            block_id = env.add_object(block_urdf, block_pose)
            p.changeVisualShape(block_id, -1, rgbaColor=block_util_colors[i] + [1])
            if i == 0:
                block_pts[block_id] = self.get_box_object_points(block_id)
                base_pose = block_pose
            if target_idx == 1:
                blocks.append((block_id, (0, None)))
            else:
                blocks.append((block_id, (np.pi / 2, None)))

        # Add zones.
        zone_size = (0.1, 0.1, 0)
        zone_poses = []
        for i in range(n_zones):
            zone_pose = self.get_random_pose(env, zone_size)
            zone_obj_id = env.add_object('zone/zone.urdf', zone_pose, 'fixed')
            p.changeVisualShape(zone_obj_id, -1, rgbaColor=zone_util_colors[i] + [1])
            zone_poses.append(zone_pose)
            # zone_poses.append((zone_obj_id, (0, None)))

        if target_objs[target_idx] == "block":
            place_pos = [(0, 0, 0.03), (0, 0, 0.08)]
            targets = [(utils.apply(base_pose, i), base_pose[1]) for i in place_pos]
            self.goals.append((blocks[:2], np.eye(2),
                               targets, False, True, 'pose', None, 1))
            self.lang_goals.append(self.lang_template.format(pick_color=block_colors[0],
                                                             place_color=block_colors[1],
                                                             place=target_objs[target_idx]))
        elif target_objs[target_idx] == "bowl":
            # target_matrix = np.zeros((n_blocks, n_bowls))
            # target_matrix[0, 0] = 1
            # print(target_matrix)
            target_matrix = np.ones((1, 1))
            self.goals.append(([blocks[0]], target_matrix,
                               [bowl_poses[0]], False, True, 'pose', None, 1))
            self.lang_goals.append(self.lang_template.format(pick_color=block_colors[0],
                                                             place_color=bowl_colors[0],
                                                             place=target_objs[target_idx]))
        else:
            target_matrix = np.ones((1, 1))
            self.goals.append(([blocks[0]], target_matrix,
                               [zone_poses[0]], True, False, 'zone',
                               (block_pts, [(zone_poses[0], zone_size)]), 1))
            self.lang_goals.append(self.lang_template.format(pick_color=block_colors[0],
                                                             place_color=zone_colors[0],
                                                             place=target_objs[target_idx]))

    def get_colors(self):
        return utils.TRAIN_COLORS if self.mode == 'train' else utils.EVAL_COLORS


class PutEvenBlockInCorrespondingZone(Task):
    """Put the blocks of an even number in the zone with the corresponding color base class and task. """

    def __init__(self):
        super().__init__()
        self.max_steps = 10
        self.pos_eps = 0.05
        self.lang_template = "put the blocks of an even number in the zone " \
                             "with the corresponding color"
        self.task_completed_desc = "done placing blocks in the zone."

    def reset(self, env):
        super().reset(env)
        n_blocks = random.randint(2, 5)
        n_blocks = 4
        n_colors = 2

        all_color_names = self.get_colors()
        selected_color_names = random.sample(all_color_names, n_blocks)
        colors = [utils.COLORS[cn] for cn in selected_color_names]

        # all_corner_names = ['bottom right corner', 'bottom side', 'bottom left corner']
        # all_corner_target_pos = [(0.65, 0.35, 0), (0.5, 0.25, 0), (0.35, 0.35, 0)]
        # all_corner_size = [(0.2, 0.3, 0), (0.5, 0.3, 0), (0.2, 0.3, 0)]
        # corner_idx = random.sample(range(len(all_corner_names)), 1)[0]

        # Add blocks.
        blocks = []
        block_pts = {}
        block_size = (0.04, 0.04, 0.04)
        block_urdf = 'stacking/block.urdf'
        block_id_list = []
        block_color_names = []
        for i in range(n_blocks):
            block_pose = self.get_random_pose(env, block_size)
            block_id = env.add_object(block_urdf, block_pose)
            block_id_list.append(block_id)
            p.changeVisualShape(block_id, -1, rgbaColor=colors[i % n_colors] + [1])
            block_color_names.append(selected_color_names[i % n_colors])
            block_pts[block_id] = self.get_box_object_points(block_id)
            blocks.append((block_id, (0, None)))

        # Add zone
        zone_size = (0.15, 0.15, 0)
        zone_poses = []
        for i in range(n_colors):
            zone_pose = self.get_random_pose(env, zone_size)
            # print("haha zone_pose", zone_pose)
            zone_obj_id = env.add_object('zone/zone.urdf', zone_pose, 'fixed')
            p.changeVisualShape(zone_obj_id, -1, rgbaColor=colors[i] + [1])
            zone_poses.append(zone_pose)

        self.scene_description = f"On the table, there are {n_blocks} blocks. Their colors are {block_color_names}. " \
                                 f"There are two zones. Their colors are {selected_color_names[:2]}. "

        # Goal: put each block in the corner.
        if n_blocks % 2 == 0:
            selected_block_pts_0 = {k: block_pts[k] for k in block_id_list[::2]}
            selected_block_pts_1 = {k: block_pts[k] for k in block_id_list[1::2]}

            self.goals.append((blocks[::2], np.ones((n_blocks // 2, 1)), [zone_poses[0]],
                               True, False, 'zone',
                               (selected_block_pts_0, [(zone_poses[0], zone_size)]), 1))
            self.goals.append((blocks[1::2], np.ones((n_blocks // 2, 1)), [zone_poses[1]],
                               True, False, 'zone',
                               (selected_block_pts_1, [(zone_poses[1], zone_size)]), 1))
        else:
            if n_blocks == 3:
                selected_blocks = [blocks[0], blocks[2]]
                selected_block_pts = {k: block_pts[k] for k in [block_id_list[0], block_id_list[2]]}
                selected_zone = zone_poses[0]
                match_matrix = np.ones((2, 1))
            elif n_blocks == 5:
                selected_blocks = [blocks[1], blocks[3]]
                selected_block_pts = {k: block_pts[k] for k in [block_id_list[1], block_id_list[3]]}
                selected_zone = zone_poses[1]
                match_matrix = np.ones((2, 1))
            else:
                raise ValueError("block number is wrong")
            self.goals.append((selected_blocks, match_matrix, [selected_zone],
                               True, False, 'zone',
                               (selected_block_pts, [(selected_zone, zone_size)]), 1))

        self.lang_goals.append(self.lang_template)

        # Only one mistake allowed.
        self.max_steps = len(blocks) + 1

    def get_colors(self):
        return utils.TRAIN_COLORS if self.mode == 'train' else utils.EVAL_COLORS
