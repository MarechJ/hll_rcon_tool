import re
from typing import Any, Callable

from rcon.message_variables import format_message_string

ARG_RE = re.compile(r"\$(\d+)")


def replace_params(ctx: dict[str, str], args: list[str], v: Any) -> Any:
    """
    Replaces arguments (from args) and message parameters (from ctx) into the provided parameter value (v).
    The parameter value can be a str, list or dict, the arguments and message parameters are going to be replaced at
    any appropriate value:
    * in lists: for each element of the list; if a list item is a list or dict, each item is processed independently to
      ensure nested values are covered as well
    * in dicts: for each value, but not for keys. If a value is a list or dict, it is going to be processed independently
      just like list items are as well.
    The return value has the same type as the passed in value, just with all arguments in values being replaced with their
    expected context or parameters.
    :param ctx:
    :param args:
    :param v:
    :return:
    """
    def do(value: Any, modifier: Callable[[str], str]) -> Any:
        if isinstance(value, str):
            value = format_message_string(modifier(value), context=ctx)
        elif isinstance(value, list):
            for li, lv in enumerate(value):
                value[li] = replace_params(ctx, args, lv)
        elif isinstance(value, dict):
            for k in value:
                kv = value[k]
                value[k] = replace_params(ctx, args, kv)
        return value

    if len(args) == 0:
        v = do(v, lambda d: d)
    for i, a in enumerate(args):
        v = do(v, lambda d: d.replace(f"${i + 1}", a))
    return v

def max_arg_index(p: Any) -> int:
    """
    Counts the highest argument index that occurs in any value. If $2 and $5 is used in any of the values, the return
    value of this function will be 5.
    Each item of a list, as well as each value of a dict key-value pair, is evaluated independently and the highest
    argument index is returned from any nested value.
    :param p:
    :return:
    """
    max_count = 0
    if isinstance(p, list):
        for v in p:
            a = max_arg_index(v)
            if a > max_count:
                max_count = a
    elif isinstance(p, str):
        for a in ARG_RE.findall(p):
            if int(a) > max_count:
                max_count = int(a)
    elif isinstance(p, dict):
        for k in p:
            v = p[k]
            a = max_arg_index(v)
            if a > max_count:
                max_count = a

    return max_count
