def fix_value_between(value: int, min_value: int, max_value: int):
    return max(min(value, max_value), min_value)
