LISTBOX_MIMETYPE = "application/x-item"

OP_NODE_IN = 1
OP_NODE_OUT = 2
OP_NODE_ADD = 3
OP_NODE_SUBTRACT = 4
OP_NODE_MULTIPLY = 5
OP_NODE_DIVIDE = 6

BLOCKS = {
}


class BlockConfigException(Exception):
    pass


class InvalidNodeRegistration(BlockConfigException):
    pass


def registerNode(operationCode, referenceClass):
    if operationCode in BLOCKS:
        raise InvalidNodeRegistration(f"Duplicite node registration of {operationCode}. "
                                      f"{BLOCKS[operationCode]} already registered.")
    BLOCKS[operationCode] = referenceClass
