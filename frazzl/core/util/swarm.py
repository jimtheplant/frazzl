import hashlib


def get_hashed_app_name(app_name):
    return str(hashlib.sha1(app_name.encode('utf-8')).hexdigest())


def _update_dict(old_dict, new_dict):
    combined = {}
    for key, value in old_dict.items():
        if key not in new_dict.keys():
            combined[key] = value
            continue
        new_value = new_dict[key]
        if type(new_value) is dict and type(value) is dict:
            _update_dict(value, new_value)
        combined[key] = new_value
    for key, value in new_dict.items():
        if key in old_dict.keys():
            continue
        combined[key] = value
    return combined


def update_swarm_definition(original_definition, new_definition):
    return _update_dict(original_definition, new_definition)
