def exclude_keys(d: dict, blacklist: set[str]) -> dict:
    return {key: value for key, value in d.items() if key not in blacklist}
