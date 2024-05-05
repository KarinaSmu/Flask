from enum import Enum


class OrderStatus(str, Enum):
    processing = "in progress"
    cancelled = "cancel"
    completed = "done"
