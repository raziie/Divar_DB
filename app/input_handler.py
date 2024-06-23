import re


def convert_all_todict():
    pass


def convert_to_dict(input_obj, attributes, drops):
    out = {}
    for i in range(len(input_obj)):
        attr = attributes[i]
        if i not in drops:
            if input_obj[i] is None:
                out[attr] = ''
            else:
                out[attr] = input_obj[i]
    return out


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


def handle_null_float(in_str):
    if in_str == '':
        return None
    else:
        return float(in_str)


def email_checker(email):
    if email is not None:
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        return re.fullmatch(email_regex, email)
    else:
        return True


def phone_checker(phone):
    if phone is not None:
        phone_regex = "^\\+?\\d{1,4}?[-.\\s]?\\(?\\d{1,3}?\\)?[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,9}$"
        return re.fullmatch(phone_regex, phone)
    else:
        return True


def images_path_handler(images):
    if images is not None:
        return images
    else:
        return []

