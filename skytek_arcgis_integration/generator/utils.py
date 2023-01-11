import string


def ask_user(prompt, default=None):
    if default:
        message = f"{prompt} [{default}]: "
    else:
        message = f"{prompt}: "

    raw_value = input(message)
    if default and raw_value == "":
        raw_value = default
    return raw_value


def replace_all(value, search_list, replacement):
    for search in search_list:
        value = value.replace(search, replacement)
    return value


NAME_UNFRIENDLY_CHARS = " /+=-@#$%&*\\|()[],."


def make_python_style_variable_name(name):
    name = replace_all(name, NAME_UNFRIENDLY_CHARS, "_")
    output = ""
    for previous_letter, letter in zip("_" + name, name):
        if letter == "_" and output[-1:] == "_":
            continue

        if (
            letter in string.ascii_uppercase
            and previous_letter in string.ascii_lowercase
        ):
            output += "_"

        output += letter.lower()

    while output[-1] == "_":
        output = output[:-1]

    while output[0] == "_":
        output = output[1:]

    return output


def make_python_style_class_name(name):
    name = replace_all(name, NAME_UNFRIENDLY_CHARS, "_")
    output = ""
    for previous_letter, letter in zip("_" + name, name):
        if letter in string.ascii_letters + string.digits:
            if previous_letter not in string.ascii_letters:
                output += letter.upper()
            else:
                output += letter.lower()

    return output
