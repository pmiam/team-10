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
    shape: tuple[int, int]
    dtype: str


def normalize_image(data: np.ndarray) -> np.ndarray:
    return (data - np.min(data)) / np.ptp(data)


def select_samples_grain_size():
    pass


@operator
def segmenter(
    inputs: BytesMessage | None, parameters: dict[str, Any]
) -> BytesMessage | None:
    if not inputs:
        return None

    other_metadata = OtherMetadata(**inputs.header.meta)

    data = np.frombuffer(inputs.data, dtype=other_metadata.dtype).reshape(
        other_metadata.shape
    )

    if data.ndim == 3:
        data = data[0]

    assert data.ndim == 2, f"Data must be 2D, got {data.ndim}D data"

    data = normalize_image(data)

    mask, embedding, bounding_boxes = segment_cellular_image(data)
