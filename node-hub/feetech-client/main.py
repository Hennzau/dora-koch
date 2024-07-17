"""
Feetech Client: This node is used to represent a chain of feetech motors. It can be used to read positions,
velocities, currents, and set goal positions and currents.
"""

import os
import argparse
import json

import pyarrow as pa

from dora import Node

from common.feetech_bus import FeetechBus, TorqueMode


class Client:

    def __init__(self, config: dict[str, any]):
        self.config = config

        description = {}
        for i in range(len(config["ids"])):
            description[config["joints"][i]] = (config["ids"][i], config["models"][i])

        self.bus = FeetechBus(config["port"], description)

        # Set client configuration values

        try:
            self.bus.write_torque_enable(config["torque"], self.config["joints"])
        except Exception as e:
            print("Error writing torque status:", e)

        self.node = Node(config["name"])

    def run(self):
        for event in self.node:
            event_type = event["type"]

            if event_type == "INPUT":
                event_id = event["id"]

                if event_id == "pull_position":
                    self.pull_position(self.node, event["metadata"])
                elif event_id == "pull_velocity":
                    self.pull_velocity(self.node, event["metadata"])
                elif event_id == "pull_current":
                    self.pull_current(self.node, event["metadata"])
                elif event_id == "write_goal_position":
                    self.write_goal_position(event["value"])
                elif event_id == "end":
                    break

            elif event_type == "ERROR":
                raise ValueError("An error occurred in the dataflow: " + event["error"])

    def close(self):
        self.bus.write_torque_enable(TorqueMode.DISABLED, self.config["joints"])

    def pull_position(self, node, metadata):
        try:
            node.send_output(
                "position",
                pa.array([self.bus.read_position(self.config["joints"])]),
                metadata
            )

        except ConnectionError as e:
            print("Error reading position:", e)

    def pull_velocity(self, node, metadata):
        try:
            node.send_output(
                "velocity",
                pa.array([self.bus.read_velocity(self.config["joints"])]),
                metadata
            )
        except ConnectionError as e:
            print("Error reading velocity:", e)

    def pull_current(self, node, metadata):
        try:
            node.send_output(
                "current",
                pa.array([self.bus.read_current(self.config["joints"])]),
                metadata
            )
        except ConnectionError as e:
            print("Error reading current:", e)

    def write_goal_position(self, goal_position_with_joints: pa.Array):
        try:
            joints = goal_position_with_joints[0]["joints"].values
            goal_position = goal_position_with_joints[0]["positions"].values

            self.bus.write_goal_position(goal_position, joints)
        except ConnectionError as e:
            print("Error writing goal position:", e)


def main():
    # Handle dynamic nodes, ask for the name of the node in the dataflow
    parser = argparse.ArgumentParser(
        description="Feetech Client: This node is used to represent a chain of feetech motors. "
                    "It can be used to read "
                    "positions, velocities, currents, and set goal positions and currents.")

    parser.add_argument("--name", type=str, required=False, help="The name of the node in the dataflow.",
                        default="feetech_client")
    parser.add_argument("--port", type=str, required=False, help="The port of the feetech motors.", default=None)
    parser.add_argument("--config", type=str, help="The configuration of the feetech motors.", default=None)

    args = parser.parse_args()

    # Check if port is set
    if not os.environ.get("PORT") and args.port is None:
        raise ValueError(
            "The port is not set. Please set the port of the feetech motors in the environment variables or as an "
            "argument.")

    port = os.environ.get("PORT") if args.port is None else args.port

    # Check if config is set
    if not os.environ.get("CONFIG") and args.config is None:
        raise ValueError(
            "The configuration is not set. Please set the configuration of the feetech motors in the environment "
            "variables or as an argument.")

    with open(os.environ.get("CONFIG") if args.config is None else args.config) as file:
        config = json.load(file)

    joints = config.keys()

    # Create configuration
    bus = {
        "name": args.name,
        "port": port,  # (e.g. "/dev/ttyUSB0", "COM3")
        "ids": [config[joint]["id"] for joint in joints],
        "joints": pa.array(joints, pa.string()),
        "models": [config[joint]["model"] for joint in joints],

        "torque": [TorqueMode.ENABLED if config[joint]["torque"] else TorqueMode.DISABLED for joint in joints],
    }

    print("Feetech Client Configuration: ", bus, flush=True)

    client = Client(bus)
    client.run()
    client.close()


if __name__ == '__main__':
    main()