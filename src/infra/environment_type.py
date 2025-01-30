from enum import Enum


class EnvironmentType(str, Enum):
    DEV = "development"
    PROD = "production"
    TEST = "test"
