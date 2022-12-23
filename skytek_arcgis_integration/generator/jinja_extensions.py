from jinja2.ext import Extension

from skytek_arcgis_integration.utils import is_numeric


def literal(value):
    if value is None or value == "None":
        return "None"

    if isinstance(value, (float, int)) or is_numeric(value):
        return str(value)

    if isinstance(value, bool) or value in ("True", "False"):
        return "True" if value else "False"

    if isinstance(value, dict):
        return (
            "{"
            + ", ".join(literal(k) + ": " + literal(v) for k, v in value.items())
            + ",}"
        )

    return '"' + str(value).replace('"', '\\"') + '"'


def kwargs(value):
    if not value:
        return ""
    assert isinstance(value, (dict))

    return ", ".join(str(k) + "=" + literal(v) for k, v in value.items()) + ","


class GeneratorExtension(Extension):
    def __init__(self, environment):
        super().__init__(environment)
        environment.filters["literal"] = literal
        environment.filters["kwargs"] = kwargs
