from enum import Enum
from typing import Any

import numpy as np
from cellSAM import segment_cellular_image
from core.models.messages import BytesMessage

from operators.operator import operator


def select_samples_grain_size(mask):
    pass


def select_samples_grain_boundaries(mask):
    pass


class MethodSelection(str, Enum):
    GRAIN_SIZE = "select_samples_grain_size"
    GRAIN_BOUNDARIES = "select_samples_grain_boundaries"


@operator
def mask_operation(
    inputs: BytesMessage | None, parameters: dict[str, Any]
) -> BytesMessage | None:
    if inputs is None:
        return None

    other_metadata = OtherMetadata(**inputs.header.meta)
    mask = np.frombuffer(inputs.data, dtype=other_metadata.dtype).reshape(
        other_metadata.shape
    )

    param_method: MethodSelection = parameters.get(
        "mask_function", MethodSelection.GRAIN_BOUNDARIES
    )

    method_map: dict[MethodSelection, Any] = {
        MethodSelection.GRAIN_SIZE: select_samples_grain_size,
        MethodSelection.GRAIN_BOUNDARIES: select_samples_grain_size,
    }
    method = method_map[param_method]

    output = method(mask)

    meta = OtherMetadata(
        path=other_metadata.path, shape=data.shape, dtype=str(data.dtype)
    )
    header = inputs.header
    header.meta.update(meta.model_dump())
    normalize = parameters.get("normalize", True)

    print(f"Segmenting image with parameters: {parameters}")
    mask, _, _ = segment_cellular_image(data, normalize=normalize)
    return BytesMessage(header=header, data=mask.tobytes())
