import ast
import re
from enum import Enum
from typing import Callable


class ActionError(Enum):
    UNKNOWN = "UNKNOWN"
    ELEMENT_ID_NOT_FOUND = "ELEMENT_ID_NOT_FOUND"
    INVALID_ELEMENT_ID = "INVALID_ELEMENT_ID"
    INVISIBLE_ELEMENT = "INVISIBLE_ELEMENT"
    UNEXPECTED_ELEMENT_TYPE = "UNEXPECTED_ELEMENT_TYPE"
    EMPTY_ACTION = "EMPTY_ACTION"
    INVALID_ACTION_TYPE = "INVALID_ACTION_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    UNEXPECTED_KEYWORD = "UNEXPECTED_KEYWORD"
    MULTIPLE_ACTIONS = "MULTIPLE_ACTIONS"
    OPTION_NOT_FOUND = "OPTION_NOT_FOUND"
    TIMEOUT = "TIMEOUT"
    NO_STATE_CHANGE = "NO_STATE_CHANGE"


_ERROR_MESSAGE = {
    "ValueError: Could not find element with bid ": ActionError.ELEMENT_ID_NOT_FOUND,
    "ValueError: expected a string, got ": ActionError.INVALID_ELEMENT_ID,
    "element is not visible": ActionError.INVISIBLE_ELEMENT,
    "Error: Error: Element is not a": ActionError.UNEXPECTED_ELEMENT_TYPE,
    "ValueError: Received an empty action.": ActionError.EMPTY_ACTION,
    "NameError: Invalid action type": ActionError.INVALID_ACTION_TYPE,
    "Malformed value": ActionError.INVALID_VALUE,
    "required positional argument": ActionError.INVALID_VALUE,
    "got an unexpected keyword argument": ActionError.UNEXPECTED_KEYWORD,
    "ValueError: Received a multi-action, only single-actions are allowed.": ActionError.MULTIPLE_ACTIONS,
    "did not find some options": ActionError.OPTION_NOT_FOUND,
    "TimeoutError: ": ActionError.TIMEOUT,
}

READABLE_ERROR_MESSAGES = {
    ActionError.UNKNOWN: "Unknown error.",
    ActionError.ELEMENT_ID_NOT_FOUND: "No element matches the provided bid.",
    ActionError.INVALID_ELEMENT_ID: "Invalid bid type. bid needs to be a string.",
    ActionError.INVISIBLE_ELEMENT: "The element is not visible.",
    ActionError.UNEXPECTED_ELEMENT_TYPE: "The type of the element is not supported for this action.",
    ActionError.EMPTY_ACTION: "Invalid action.",
    ActionError.INVALID_ACTION_TYPE: "Invalid action type.",
    ActionError.INVALID_VALUE: "Invalid argument.",
    ActionError.UNEXPECTED_KEYWORD: "Unexpected keyword argument in the function call.",
    ActionError.MULTIPLE_ACTIONS: "Received a multi-action, only single-actions are allowed.",
    ActionError.OPTION_NOT_FOUND: "The option is not found.",
    ActionError.TIMEOUT: "Executed.",
}

COORD_ACTION_TYPES = set(
    [
        "mouse_move",
        "mouse_up",
        "mouse_down",
        "mouse_click",
        "mouse_dblclick",
        "mouse_upload_file",
        "mouse_drag_and_drop",
    ]
)


def determine_error_type(action_error: str) -> ActionError:
    for message in _ERROR_MESSAGE:
        if message in action_error:
            return _ERROR_MESSAGE[message]
    return ActionError.UNKNOWN


def clean_action(action: str | None) -> str:
    """Removes quotes and numbers wrapping the action.

    For example, given
    ```
    click("123")
    ```
    the function will return
    click("123")

    If the action is None, the function will return an empty string.
    """
    if action is None:
        return ""
    action_lines = action.split("\n")
    actions = []
    for line in action_lines:
        if line.startswith("```") and line.endswith("```"):
            action = line.strip("```")
        else:
            # remove markdown
            if len(line.strip()) == 0 or line.startswith("```"):
                continue
            action = line.strip()
            action = re.sub(r"'\[(\d+)\]'", r"'\1'", action)
            action = re.sub(r"\[(\d+)\]", r"'\1'", action)
        actions.append(action)
    return "\n".join(actions)


def remove_thinking(response, cot_open_tag="<thinking>", cot_close_tag="</thinking>"):
    # Remove content between COT tags from the response
    response = re.sub(rf"{cot_open_tag}[\W\w]*?{cot_close_tag}", "", response)
    return response


def get_action_type(action_string):
    return action_string[: action_string.find("(")].strip()


def extract_coord(action_str) -> tuple[float, float] | None:
    action_type = get_action_type(action_str)
    if not action_type in COORD_ACTION_TYPES:
        return None
    action_str = action_str[action_str.find("(") + 1 :].strip()
    x = action_str[: action_str.find(",")]
    action_str = action_str[action_str.find(",") + 1 :]
    if action_str.find(",") < action_str.find(")"):
        y = action_str[: action_str.find(",")]
    else:
        y = action_str[: action_str.find(")")]
    return float(x), float(y)


def transform_coordinates(
    action_str: str, transform: Callable[[float, float], tuple[float, float]]
):
    """Transforms coordinates in Python calls."""
    tree = ast.parse(action_str)
    for body in tree.body:
        action_type = body.value.func.id
        if not (action_type.startswith("mouse_") or action_type == "scroll"):
            continue
        body.value.args[0].value, body.value.args[1].value = transform(
            body.value.args[0].value, body.value.args[1].value
        )
        if action_type == "mouse_drag_and_drop":
            body.value.args[2].value, body.value.args[3].value = transform(
                body.value.args[2].value, body.value.args[3].value
            )
    return ast.unparse(tree)


def normalize_coordinates(
    action_str: str,
    viewport_width: float = 1280,
    viewport_height: float = 720,
    ndigits: int = 4,
) -> str:
    """Normalizes coordinates in Python call string."""

    def transform(x: float, y: float) -> tuple[float, float]:
        return round(x / viewport_width, ndigits), round(y / viewport_height, ndigits)

    try:
        return transform_coordinates(action_str, transform)
    except Exception as e:
        return action_str


def extract_parameter(call_str: str, parameter_index: int = 0) -> str:
    """
    Extracts a parameter from a Python function call given as a string.
    """
    try:
        # Parse the string in 'eval' mode so that it expects a single expression.
        node = ast.parse(call_str, mode="eval")
    except SyntaxError as e:
        raise ValueError("Invalid Python expression") from e

    # Check that the parsed expression is a function call.
    if not isinstance(node.body, ast.Call):
        raise ValueError("The provided string does not represent a function call.")

    call_node = node.body

    if call_node.keywords:
        param = call_node.keywords[parameter_index]
    elif call_node.args:
        param = call_node.args[parameter_index]
    else:
        # No parameters were provided.
        return ""

    return ast.unparse(param)


