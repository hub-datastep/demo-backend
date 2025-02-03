from uuid import uuid4


def generate_uuid() -> str:
    """
    Generates a random UUID4 string.
    """
    return str(uuid4())
