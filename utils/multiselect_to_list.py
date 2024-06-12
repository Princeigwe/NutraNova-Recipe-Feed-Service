def multiselect_to_list(preference):
    """Convert multi-select user preferences from string to list data type, if it's of string type."""
    if isinstance(preference, list):
        return preference
    elif isinstance(preference, str):
        if preference:
            return preference.split(",") if "," in preference else [preference]
        else:
            return []
    return []