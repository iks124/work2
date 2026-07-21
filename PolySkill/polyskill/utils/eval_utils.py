import pandas as pd
import re
from typing import Any, Callable


def mark_predictions_and_calculate_accuracy(
    df: pd.DataFrame,
    metric_fn: Callable[[Any, Any], bool] = lambda x, y: x == y,
    label_column: str = "label",
    prediction_column: str = "prediction",
    output_column: str = "correct",
):
    """
    Mark the predictions in the DataFrame as correct or incorrect based on a metric function
    and calculate the accuracy.

    Args:
        df (pd.DataFrame): The DataFrame containing the data to evaluate.
            The provided label_column, prediction_column, and output_column must be present.
        metric_fn (Callable[..., bool]): The metric function to use for comparison.
            The function should take two arguments and return a boolean.
            Default is a function that checks for equality.
        label_column (str): The name of the column containing the true labels. Default is 'answer'.
        prediction_column (str): The name of the column containing the predictions. Default is 'prediction'.
        output_column (str): The name of the column to store the correctness. Default is 'correct'.

    Returns:
        float: The accuracy

    Raises:
        ValueError: If the DataFrame does not contain the specified columns
        ValueError: If the DataFrame already contains the output column
    """
    if (label_column not in df.columns) or (prediction_column not in df.columns):
        raise ValueError(
            "The DataFrame must contain the column '{}', and '{}'".format(
                label_column,
                prediction_column,
            )
        )
    if output_column in df.columns:
        raise ValueError(
            "The DataFrame already contains the column '{}'. Doing so will override this column".format(
                output_column
            )
        )

    df[output_column] = df.apply(
        lambda row: metric_fn(row[label_column], row[prediction_column]), axis=1
    ).astype(int)
    accuracy = df[output_column].mean()
    return accuracy


def extract_bbox_from_string(sentence: str) -> tuple[float, float, float, float] | None:
    """
    Extract the bounding box coordinates from a string and return them as a tuple of floats.

    Args:
        sentence (str): The string to search for bounding box coordinates

    Returns:
        Optional[tuple[float, float, float, float]]: The bounding box coordinates as a tuple of floats if found,
            else None
    """
    pattern = (
        r"\((\-?\d+\.?\d*),\s*(\-?\d+\.?\d*),\s*(\-?\d+\.?\d*),\s*(\-?\d+\.?\d*)\)"
    )

    # Search for the pattern in the string
    match = re.search(pattern, sentence)

    if match:
        # Extract the matched groups and convert them to float or int
        elements = []
        for i in range(1, 5):
            element = float(match.group(i))
            elements.append(element)
        return tuple(elements)
    else:
        return None  # Return None if no match is found
