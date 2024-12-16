import multiprocessing
import pathlib
import time
from typing import cast

import DTMicroscope
import DTMicroscope.server.server_afm
import numpy as np
import Pyro5.api
import Pyro5.errors
import pytest
import SciFiReaders as sr
import sidpy
from DTMicroscope.server.server_afm import main_server

HERE = pathlib.Path(__file__).parent
DATA_DIR = (
    HERE.parent / "thirdparty" / "rama-data" / "TopoForHack" / "material1_perovksite"
)
filenames = DATA_DIR.glob("*.h5")
H5_FILES = cast(list, cast(str, [str(DATA_DIR / f) for f in filenames]))


@pytest.fixture(scope="module")
def run_server():
    process = multiprocessing.Process(target=main_server)
    process.start()
    try:
        yield
    finally:
        process.terminate()
        process.join()


def test_load_data(run_server):
    uri = "PYRO:microscope.server@localhost:9092"
    mic_server = Pyro5.api.Proxy(uri)
    mic_server = cast(DTMicroscope.server.server_afm.MicroscopeServer, mic_server)

    retries = 0
    max_retries = 5
    while True:
        try:
            mic_server.initialize_microscope("AFM", data_path=str(H5_FILES[0]))
            break
        except Pyro5.errors.CommunicationError:
            retries += 1
            time.sleep(1)
            if retries > max_retries:
                raise
    mic_server.setup_microscope()
    info = mic_server.get_dataset_info()
    mic_server.go_to(0, 5)
    print(info)


def test_load_numpy_array():
    for file_path in H5_FILES[1:]:
        reader = sr.NSIDReader(file_path)
        data = reader.read()
        data = cast(sidpy.Dataset, data["Channel_000"])
        arr = np.array(data[:])
        assert isinstance(arr, np.ndarray)
