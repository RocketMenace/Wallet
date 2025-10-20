from enum import Enum


class OperationType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
