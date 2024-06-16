def handle_null_str(in_str):
    if in_str == '':
        return None
    else:
        return str(in_str)


def handle_null_int(in_str):
    if in_str == '':
        return None
    else:
        return int(in_str)
