import pyarrow as pa
import pyarrow.compute as pc


def joints_values_to_arrow(joints, values):
    return pa.StructArray.from_arrays(
        arrays=[joints, values],
        names=["joints", "values"],
        fields=None,
        mask=None,
        memory_pool=None,
    )


def physical_to_logical(physical_position: pa.StructArray, table: {}) -> pa.StructArray:
    joints = physical_position.field("joints")
    positions = physical_position.field("values")

    result = []

    for i in range(len(joints)):
        if joints[i].as_py() in table:
            result.append(
                table[joints[i].as_py()]["physical_to_logical"](
                    (positions[i].as_py() % 4096) * 360 / 4096
                )
                if positions[i].as_py() is not None
                else None
            )

    return joints_values_to_arrow(joints, pa.array(result, type=pa.float32()))


def logical_to_physical(logical_position: pa.StructArray, table: {}) -> pa.StructArray:
    joints = physical_position.field("joints")
    positions = physical_position.field("values")

    result = []

    for i in range(len(joints)):
        if joints[i].as_py() in table:
            result.append(
                int(
                    table[joints[i].as_py()]["logical_to_physical"](
                        positions[i].as_py()
                        if positions[i].as_py() is not None
                        else None
                    )
                    * 4096
                    / 360
                )
                if positions[i].as_py() is not None
                else None
            )

    return joints_values_to_arrow(joints, pa.array(result, type=pa.int32()))


def compute_goal_with_offset(
    physical_position: pa.StructArray, logical_goal: pa.StructArray, table: {}
):
    joints = physical_position.field("joints")

    goal = logical_to_physical(logical_goal, table)

    base = logical_to_physical(physical_to_logical(physical_position, table), table)

    return joints_values_to_arrow(
        joints,
        pc.add(
            pc.subtract(physical_position["values"].values, base["values"].values),
            goal["values"].values,
        ),
    )
