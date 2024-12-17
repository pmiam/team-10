import pathlib
from typing import Any

import numpy as np
from cellSAM import segment_cellular_image
from core.logger import get_logger
from core.models.messages import BytesMessage
from operators.operator import operator
from pydantic import BaseModel, ConfigDict

logger = get_logger()


skip_counter = 0
average_counter = 0
accumulated_dense = None


class OtherMetadata(BaseModel):
    model_config: ConfigDict = ConfigDict(extra="ignore")
    path: pathlib.Path
    shape: tuple[int, ...]
    dtype: str


def normalize_image(data: np.ndarray) -> np.ndarray:
    return (data - np.min(data)) / np.ptp(data)


def str_to_bool(s):
    if isinstance(s, bool):
        return s
    if isinstance(s, str):
        return s.lower() == "true"
    raise ValueError("Input must be a string")


@operator
def segmenter(
    inputs: BytesMessage | None, parameters: dict[str, Any]
) -> BytesMessage | None:
    if inputs is None:
        return None

    other_metadata = OtherMetadata(**inputs.header.meta)
    data = np.frombuffer(inputs.data, dtype=other_metadata.dtype).reshape(
        other_metadata.shape
    )

    if data.ndim == 3:
        print("Data is 3D, selecting first channel")
        data = data[0]

    assert data.ndim == 2, f"Data must be 2D, got {data.ndim}D data"

    meta = OtherMetadata(
        path=other_metadata.path, shape=data.shape, dtype=str(data.dtype)
    )
    header = inputs.header
    header.meta.update(meta.model_dump())
    normalize = parameters.get("normalize", True)
    normalize = str_to_bool(normalize)

    print(f"Segmenting image with parameters: {parameters}")
    mask, _, _ = segment_cellular_image(data, normalize=normalize)
    return BytesMessage(header=header, data=mask.tobytes())
