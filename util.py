def toInt(bytes):
    result = 0

    for i in range(0, len(bytes)):
        result |= bytes[i] << ((len(bytes) - i - 1) * 8)

    return result


def toBytes(value):
    result = []

    while value != 0:
        result.insert(0, value & 0xFF)
        value >>= 8

    return bytes(result)
