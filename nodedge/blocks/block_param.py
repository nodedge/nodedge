from enum import IntEnum


class BlockParamType(IntEnum):
    """
    Block parameter type enumeration.
    """

    Float = 0
    Int = 1
    Bool = 2
    ShortText = 3
    LongText = 4


class BlockParam:
    def __init__(self, name, value, paramType, minValue=None, maxValue=None, step=None):
        self.name = name
        self._value = value
        self.paramType: BlockParamType = paramType
        self.minValue = minValue
        self.maxValue = maxValue
        self.step = step

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self.paramType in [BlockParamType.LongText, BlockParamType.ShortText]:
            if not isinstance(value, str):
                raise ValueError("Value must be a string")
        elif self.paramType == BlockParamType.Float:
            if not isinstance(value, float):
                raise ValueError("Value must be a float")
        elif self.paramType == BlockParamType.Int:
            if not isinstance(value, int):
                raise ValueError("Value must be an integer")
        elif self.paramType == BlockParamType.Bool:
            if not isinstance(value, bool):
                raise ValueError("Value must be a boolean")
        else:
            raise ValueError("Unknown parameter type")

        self._value = value
