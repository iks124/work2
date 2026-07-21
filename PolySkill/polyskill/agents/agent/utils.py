from faker import Faker
import numpy as np
import random
import re
from typing import List, Dict
import warnings

from polyskill.utils.image_utils import numpy_to_base64

HUMAN_DELIMITER = "\n\nHuman:"
ASSISTANT_DELIMITER = "\n\nAssistant:"


def prepare_image_input(arr):
    return {
        "type": "image_url",
        "image_url": {"url": f"data:image/png;base64,{numpy_to_base64(arr)}"},
    }


def screenshots_differ(screenshot1, screenshot2):
    return (screenshot1.shape != screenshot2.shape) or (
        screenshot1 != screenshot2
    ).any()


def prompt_to_messages(
    prompt: str,
    *,
    user_delimiter: str = HUMAN_DELIMITER,
    assistant_delimiter: str = ASSISTANT_DELIMITER,
    images: dict[str, np.ndarray] = {},
) -> list[dict]:
    """
    Converts a prompt string into a list of messages for the user and assistant.

    The user prompt can contain images and text, where images are specified as <image_KEY>, where KEY is a key in the images dictionary.

    If the prompt does not start with the user delimiter, the first part of the prompt before the user delimiter is considered a system prompt.
    """

    image_keys_unused = set(images.keys())

    def process_user_prompt(prompt):
        user_content = []
        if assistant_delimiter in prompt:
            prompt = prompt.split(assistant_delimiter)[0]

        for part in re.split(r"(<image:[^>]+>)", prompt):
            if len(part) == 0:
                continue
            if part.startswith("<image:") and part.endswith(">"):
                key = part[len("<image:") : -1]
                user_content.append(prepare_image_input(images[key]))
                image_keys_unused.discard(key)
            else:
                user_content.append({"type": "text", "text": part})

        return user_content

    messages = []
    role = "system" if not prompt.startswith(user_delimiter) else "user"
    for line in prompt.split(user_delimiter):
        if line.strip() == "":
            continue
        if role == "system":
            # System prompts are text-only
            messages.append({"role": role, "content": line})
            role = "user"
        elif role == "user":
            if assistant_delimiter in line:
                user_content, assistant_content = line.split(assistant_delimiter)
                messages.append(
                    {"role": role, "content": process_user_prompt(user_content)}
                )
                role = "assistant"
                content = []
                content.append({"type": "text", "text": assistant_content})
                messages.append({"role": role, "content": content})
                role = "user"
            else:
                user_content = process_user_prompt(line)
                messages.append({"role": role, "content": user_content})

    if len(image_keys_unused) > 0:
        warnings.warn(
            f"Unused image keys during prompt-to-messages conversion: {image_keys_unused}"
        )

    return messages


def remove_thinking(response, cot_open_tag="<thinking>", cot_close_tag="</thinking>"):
    # Remove content between COT tags from the response

    response = re.sub(rf"{cot_open_tag}[\W\w]*?{cot_close_tag}", "", response)

    return response


def draw_coordinate_lines(image, step=100, color=(255, 0, 255)):
    image = image.copy()

    # Draw horizontal lines
    for i in range(step - 1, image.shape[0], step):
        image[i, :, :] = color

    # Draw vertical lines
    for i in range(step - 1, image.shape[1], step):
        image[:, i, :] = color

    return image


def base64_to_image(b64: str):
    """Decode a base64-encoded image string into a PIL Image."""
    import base64
    import io

    from PIL import Image

    return Image.open(io.BytesIO(base64.b64decode(b64)))


def produce_fake_details(n=3):
    """Utility to produce fake details"""
    faker = Faker()
    loc = faker.local_latlng()

    data = {
        "Person name": [faker.name() for _ in range(n)],
        "Address": [faker.address() for _ in range(n)],
        "Phone number": [faker.phone_number() for _ in range(n)],
        "Email": [
            (faker.email().split("@")[0] + "@" + faker.domain_name()) for _ in range(n)
        ],
        "Date": [str(faker.date_this_decade()) for _ in range(n)],
        "Number": [str(random.randint(0, 100)) for _ in range(n)],
        "Username": [faker.user_name() for _ in range(n)],
        "Project": [f"{faker.word()}_{faker.word()}" for _ in range(n)],
        "Location": [f"{loc[2]}, {loc[3]}" for _ in range(n)],
    }
    text = ""
    for key, values in data.items():
        text += f' * {key}: {"," .join(values)}\n'
    return text
