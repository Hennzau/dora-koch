import pyarrow as pa


def physical_to_logical(physical_position: pa.Scalar, table: {}):
    joints = physical_position["joints"].values
    positions = physical_position["positions"].values

    result = []

    for i in range(len(joints)):
        if joints[i].as_py() in table:
            result.append(table[joints[i].as_py()]["physical_to_logical"](
                (positions[i].as_py() % 4096) * 360 / 4096
            ))

    return pa.scalar({
        "joints": joints,
        "positions": pa.array(result, type=pa.float32()),
    }, type=pa.struct({
        "joints": pa.list_(pa.string()),
        "positions": pa.list_(pa.float32()),
    }))


def logical_to_physical(logical_position: pa.Scalar, table: {}):
    joints = logical_position["joints"].values
    positions = logical_position["positions"].values

    result = []

    for i in range(len(joints)):
        if joints[i].as_py() in table:
            result.append(int(table[joints[i].as_py()]["logical_to_physical"](
                positions[i].as_py()
            ) * 4096 / 360))

    return pa.scalar({
        "joints": joints,
        "positions": pa.array(result, type=pa.int32()),
    }, type=pa.struct({
        "joints": pa.list_(pa.string()),
        "positions": pa.list_(pa.int32()),
    }))
