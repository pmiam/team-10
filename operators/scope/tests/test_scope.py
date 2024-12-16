import pathlib
from typing import cast
import DTMicroscope
import DTMicroscope.server.server_afm
import Pyro5.api

HERE = pathlib.Path(__file__).parent


def test_load_data():
    uri = "PYRO:microscope.server@localhost:9092"
    mic_server = Pyro5.api.Proxy(uri)
    mic_server = cast(DTMicroscope.server.server_afm.MicroscopeServer, mic_server)
    data_dir = (
        HERE.parent
        / "thirdparty"
        / "rama-data"
        / "TopoForHack"
        / "material1_perovksite"
    )
    h5_files = data_dir.glob("*.h5")
    data = [str(data_dir / f) for f in h5_files]
    mic_server.initialize_microscope("AFM", data_path=str(data[0]))
    mic_server.setup_microscope()
    info = mic_server.get_dataset_info()
    mic_server.go_to(0, 5)
    print(info)
