import os
import argparse
import json

import pyarrow as pa
import pyarrow.compute as pc

from dora import Node

from position_control.utils import (
    physical_to_logical,
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
        default="lcr-to-record",
    )
    parser.add_argument(
        "--leader-control",
        type=str,
        help="The configuration file for controlling the leader.",
        default=None,
    )
    parser.add_argument(
        "--follower-control",
        type=str,
        help="The configuration file for controlling the follower.",
        default=None,
    )

    args = parser.parse_args()

    if not os.environ.get("LEADER_CONTROL") and args.leader_control is None:
        raise ValueError(
            "The leader control is not set. Please set the configuration of the leader in the environment variables or "
            "as an argument."
        )

    if not os.environ.get("FOLLOWER_CONTROL") and args.follower_control is None:
        raise ValueError(
            "The follower control is not set. Please set the configuration of the follower in the environment "
            "variables or as an argument."
        )

    with open(
        os.environ.get("LEADER_CONTROL")
        if args.leader_control is None
        else args.leader_control
    ) as file:
        leader_control = json.load(file)

    with open(
        os.environ.get("FOLLOWER_CONTROL")
        if args.follower_control is None
        else args.follower_control
    ) as file:
        follower_control = json.load(file)

    for joint in leader_control.keys():
        leader_control[joint]["physical_to_logical"] = build_physical_to_logical(
            leader_control[joint]["physical_to_logical"]
        )
        leader_control[joint]["logical_to_physical"] = build_logical_to_physical(
            leader_control[joint]["logical_to_physical"]
        )

        follower_control[joint]["physical_to_logical"] = build_physical_to_logical(
            follower_control[joint]["physical_to_logical"]
        )
        follower_control[joint]["logical_to_physical"] = build_logical_to_physical(
            follower_control[joint]["logical_to_physical"]
        )

    node = Node(args.name)

    for event in node:
        event_type = event["type"]

        if event_type == "INPUT":
            event_id = event["id"]

            if event_id == "leader_position":
                leader_position = event["value"]

                leader_position = physical_to_logical(leader_position, leader_control)

                interpolation = pa.array([1, 1, 1, 1, 1, 700 / 450], type=pa.float32())

                logical_goal = joints_values_to_arrow(
                    leader_position.field("joints"),
                    pc.multiply(leader_position.field("values"), interpolation),
                )

                node.send_output("logical_goal", logical_goal, event["metadata"])

            elif event_id == "follower_position":
                follower_position = event["value"]

                follower_position = physical_to_logical(
                    follower_position, follower_control
                )

                node.send_output(
                    "logical_position", follower_position, event["metadata"]
                )

        elif event_type == "ERROR":
            print("[lcr-to-record] error: ", event["error"])
            break


if __name__ == "__main__":
    main()
