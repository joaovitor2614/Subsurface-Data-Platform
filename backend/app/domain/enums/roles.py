from enum import Enum


class UserRole(str, Enum):
    GEOLOGIST = "Geologist"
    RESERVOIR_ENGINEER = "Reservoir Engineer"
    ADMIN = "ADMIN"
