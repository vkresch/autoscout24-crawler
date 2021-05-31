from enum import Enum

class OnlineSince(Enum):
    ALL = ""
    DAY_1 = "1"
    DAY_2 = "2"
    DAY_3 = "3"
    DAY_4 = "4"
    DAY_5 = "5"
    DAY_6 = "6"
    DAY_7 = "7"
    DAY_14 = "14"

class VATDeductible(Enum):
    YES = "true"
    NO = ""