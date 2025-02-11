from typing import List, Optional
from circuitsvis.utils.render import RenderedHTML, render
import numpy as np


def torch_topk(x: np.ndarray, k: int, dim: int, largest: bool = True):
    # Find the indices of the top k values along axis 1
    topk_idxs = np.argpartition(x, -k, axis=dim)[:, -k:]

    # Sort the indices to get the top k indices
    topk_idxs = np.argsort(topk_idxs, axis=dim)

    # Extract the top k values
    topk_vals = np.take_along_axis(x, topk_idxs, axis=dim)

    # If you want the results in descending order, reverse the order
    if largest:
        topk_vals = topk_vals[:, ::-1]
        topk_idxs = topk_idxs[:, ::-1]

    return topk_vals, topk_idxs


def topk_tokens(
    tokens: List[List[str]],
    activations: List[np.ndarray],  # np.ndarray: [n_layers, n_tokens, n_neurons]
    max_k: int = 10,
    first_dimension_name: str = "Layer",
    third_dimension_name: str = "Neuron",
    sample_labels: Optional[List[str]] = None,
    first_dimension_labels: Optional[List[str]] = None,
) -> RenderedHTML:
    """Show a table of the topk and bottomk activations.

    The columns correspond to the given third_dimension_name.

    Includes drop-downs for all dimensions as well as options to choose the number of columns to show.

    Note that we can't set labels for the third dimension because the visualisation uses pagination on this dimension.

    Args:
        tokens: Nested list of tokens for each sample (e.g. `[["A", "person"],
        ["He" "ran"]]`)
        activations: List with the same length as tokens (indicating the number
        of samples) containing activations of the shape [n_layers x
        n_neurons x n_tokens]
        max_k: Maximum number of top and bottom activations to show. This
        prevents us sending too much data to the react component.
        first_dimension_name: Name of the first dimension (e.g. "Layer")
        third_dimension_name: Name of the third dimension (e.g. "Neuron")
        sample_labels: Optional list of labels for each sample
        first_dimension_labels: Optional list of labels for each value in the first dimension

    Returns:
        Html: Topk activations visualization
    """

    assert len(tokens) == len(activations), "tokens and activations must be same length"
    assert all(
        act.ndim == 3 for act in activations
    ), "activations must be of the form [n_layers, n_tokens, n_neurons]"

    topk_vals = []
    topk_idxs = []
    bottomk_vals = []
    bottomk_idxs = []
    for sample_acts in activations:
        # get topk tokens for each object
        # Set max_k to the min of the number of tokens and the max_k
        k = min(sample_acts.shape[1], max_k)
        sample_topk_vals, sample_topk_idxs = torch_topk(sample_acts, k, dim=1)
        # also get bottom k vals
        sample_bottomk_vals, sample_bottomk_idxs = torch_topk(
            sample_acts, k, dim=1, largest=False
        )

        # reverse sort order of bottomk vals and idxs
        sample_bottomk_vals = sample_bottomk_vals[:, ::-1]
        sample_bottomk_idxs = sample_bottomk_idxs[:, ::-1]

        topk_vals.append(sample_topk_vals.tolist())
        topk_idxs.append(sample_topk_idxs.tolist())
        bottomk_vals.append(sample_bottomk_vals.tolist())
        bottomk_idxs.append(sample_bottomk_idxs.tolist())

    return render(
        "TopkTokens",
        tokens=tokens,
        topkVals=topk_vals,
        topkIdxs=topk_idxs,
        bottomkVals=bottomk_vals,
        bottomkIdxs=bottomk_idxs,
        firstDimensionName=first_dimension_name,
        thirdDimensionName=third_dimension_name,
        sampleLabels=sample_labels,
        firstDimensionLabels=first_dimension_labels,
    )
