"""
Aloha Auto Configure: This program is used to automatically configure the (Aloha) for the user.

The program will:
1. Disable all torque motors of provided Aloha.
2. Ask the user to move the Aloha to the position 1 (see CONFIGURING.md for more details).
3. Record the position of the Aloha.
4. Ask the user to move the Aloha to the position 2 (see CONFIGURING.md for more details).
5. Record the position of the Aloha.
8. Calculate the offset and inverted mode of the Aloha.
9. Let the user verify in real time that the Aloha is working properly.

It will also enable all appropriate operating modes for the Aloha.
"""

import argparse
import time
import json

import numpy as np
import pyarrow as pa

from common.dynamixel_bus import DynamixelBus, TorqueMode, OperatingMode
from common.position_control.utils import physical_to_logical, logical_to_physical
from common.position_control.configure import build_physical_to_logical_tables, build_logical_to_physical_tables, \
    build_physical_to_logical, build_logical_to_physical

FULL_ARM = pa.array([
    "shoulder_pan",
    "shoulder_lift_1",
    "shoulder_lift_2",
    "elbow_flex_1",
    "elbow_flex_2",
    "wrist_roll_1",
    "wrist_flex",
    "wrist_roll_2",
    "gripper"
], type=pa.string())

ARM_WITHOUT_GRIPPER = pa.array([
    "shoulder_pan",
    "shoulder_lift_1",
    "shoulder_lift_2",
    "elbow_flex_1",
    "elbow_flex_2",
    "wrist_roll_1",
    "wrist_flex",
    "wrist_roll_2",
], type=pa.string())

GRIPPER = pa.array(["gripper"], type=pa.string())


def pause():
    """
    Pause the program until the user presses the enter key.
    """
    input("Press Enter to continue...")


def configure_servos(bus: DynamixelBus):
    """
    Configure the servos for the Aloha.
    :param bus: DynamixelBus
    """
    bus.write_torque_enable(TorqueMode.DISABLED, FULL_ARM)

    bus.write_operating_mode(OperatingMode.EXTENDED_POSITION, ARM_WITHOUT_GRIPPER)
    bus.write_operating_mode(OperatingMode.CURRENT_CONTROLLED_POSITION, GRIPPER)


def main():
    parser = argparse.ArgumentParser(
        description="Aloha Auto Configure: This program is used to automatically configure the Aloha for the user.")

    parser.add_argument("--port", type=str, required=True, help="The port of the Aloha.")
    parser.add_argument("--right", action="store_true", help="If the Aloha is on the right side of the user.")
    parser.add_argument("--left", action="store_true", help="If the Aloha is on the left side of the user.")
    parser.add_argument("--follower", action="store_true", help="If the Aloha is the follower of the user.")
    parser.add_argument("--leader", action="store_true", help="If the Aloha is the leader of the user.")

    args = parser.parse_args()

    if args.right and args.left:
        raise ValueError("You cannot specify both --right and --left.")

    if args.follower and args.leader:
        raise ValueError("You cannot specify both --follower and --leader.")

    wanted_position_1 = pa.array([0, -90, -90, 90, 90, 0, 0, 0, 0], type=pa.int32())
    wanted_position_2 = pa.array([90, 0, 0, 0, 0, 90, 90, 90, 90], type=pa.int32())

    wanted = pa.array([
        (wanted_position_1[i], wanted_position_2[i])

        for i in range(len(wanted_position_1))
    ])

    arm = DynamixelBus(
        args.port, {
            "shoulder_pan": (1, "x_series"),
            "shoulder_lift_1": (2, "x_series"),
            "shoulder_lift_2": (3, "x_series"),
            "elbow_flex_1": (4, "x_series"),
            "elbow_flex_2": (5, "x_series"),
            "wrist_roll_1": (6, "x_series"),
            "wrist_flex": (7, "x_series"),
            "wrist_roll_2": (8, "x_series"),
            "gripper": (9, "x_series")
        }
    )

    configure_servos(arm)

    print("Please move the Aloha to the first position.")
    pause()
    physical_position_1 = arm.read_position(FULL_ARM)["positions"].values

    print("Please move the Aloha to the second position.")
    pause()
    physical_position_2 = arm.read_position(FULL_ARM)["positions"].values

    print("Configuration completed.")

    physical_to_logical_tables = build_physical_to_logical_tables(physical_position_1, physical_position_2, wanted)
    logical_to_physical_tables = build_logical_to_physical_tables(physical_position_1, physical_position_2, wanted)

    control_table = {}
    control_table_json = {}
    for i in range(len(FULL_ARM)):
        control_table[FULL_ARM[i].as_py()] = {
            "physical_to_logical": build_physical_to_logical(physical_to_logical_tables[i]),
            "logical_to_physical": build_logical_to_physical(logical_to_physical_tables[i]),
        }

        control_table_json[FULL_ARM[i].as_py()] = {
            "id": i + 1,
            "model": "x_series",
            "torque": True if args.follower else True if args.leader and i == 5 else False,
            "goal_current": None,
            "goal_position": None,
            "physical_to_logical": physical_to_logical_tables[i],
            "logical_to_physical": logical_to_physical_tables[i],

            "P": None,
            "I": None,
            "D": None,
        }

    left = "left" if args.left else "right"
    leader = "leader" if args.leader else "follower"

    path = (input(
        f"Please enter the path of the configuration file (default is ./robots/aloha/configs/{leader}.{left}.json): ")
            or f"./robots/aloha/configs/{leader}.{left}.json")

    with open(path, "w") as file:
        json.dump(control_table_json, file)

    while True:
        base_physical_position = arm.read_position(FULL_ARM)
        logical_position = physical_to_logical(base_physical_position, control_table)

        print(
            f"Logical Position: {logical_position["positions"]}")

        time.sleep(0.5)


if __name__ == "__main__":
    main()
