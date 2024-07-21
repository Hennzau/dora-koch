import os
import argparse
import json

import numpy as np
import pyarrow as pa
import pyarrow.compute as pc

from dora import Node

from position_control.utils import (
    physical_to_logical,
    compute_goal_with_offset,
    joints_values_to_arrow,
)

from position_control.configure import (
    build_logical_to_physical,
    build_physical_to_logical,
)


def main():
    parser = argparse.ArgumentParser(
        description="Interpolation LCR Node: This Dora node is used to calculates appropriate goal positions for the "
        "LCR followers knowing a Leader position and Follower position."
    )

    parser.add_argument(
        "--name",
        type=str,
        required=False,
        help="The name of the node in the dataflow.",
        default="lcr-to-simu-lcr",
    )
    parser.add_argument(
        "--leader-control",
        type=str,
        help="The configuration file for controlling the leader.",
        default=None,
    )

    args = parser.parse_args()

    if not os.environ.get("LEADER_CONTROL") and args.leader_control is None:
        raise ValueError(
            "The leader control is not set. Please set the configuration of the leader in the environment variables or "
            "as an argument."
        )

    with open(
        os.environ.get("LEADER_CONTROL")
        if args.leader_control is None
        else args.leader_control
    ) as file:
        leader_control = json.load(file)

    for joint in leader_control.keys():
        leader_control[joint]["physical_to_logical"] = build_physical_to_logical(
            leader_control[joint]["physical_to_logical"]
        )
        leader_control[joint]["logical_to_physical"] = build_logical_to_physical(
            leader_control[joint]["logical_to_physical"]
        )

    logical_leader_initial_goal = joints_values_to_arrow(
        leader_control.keys(),
        [leader_control[joint]["goal_position"] for joint in leader_control.keys()],
    )

    node = Node(args.name)

    leader_initialized = False

    for event in node:
        event_type = event["type"]

        if event_type == "INPUT":
            event_id = event["id"]

            if event_id == "leader_position":
                leader_position = event["value"]

                if not leader_initialized:
                    leader_initialized = True

                    physical_goal = compute_goal_with_offset(
                        leader_position, logical_leader_initial_goal, leader_control
                    )

                    node.send_output("leader_goal", physical_goal, event["metadata"])

                leader_position = physical_to_logical(leader_position, leader_control)

                interpolation_m = pa.array(
                    [
                        np.pi / 180,
                        np.pi / 180,
                        np.pi / 180,
                        np.pi / 180,
                        np.pi / 180,
                        np.pi / 180 * 700 / 450,
                    ],
                    type=pa.float32(),
                )

                interpolation_a = pa.array([0, 0, 0, 0, 90, 0], type=pa.float32())

                logical_goal = joints_values_to_arrow(
                    leader_position.field("joints"),
                    pc.multiply(
                        pc.add(leader_position.field("values"), interpolation_a),
                        interpolation_m,
                    ),
                )

                node.send_output("follower_goal", logical_goal, event["metadata"])

        elif event_type == "ERROR":
            print("[lcr-to-simu] error: ", event["error"])
            break


if __name__ == "__main__":
    main()
