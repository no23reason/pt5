from pt5_core.ncp_model import NcpFile


def test_ncp_to_model_1(simple_ncp, snapshot):
    parsed = NcpFile.parse(simple_ncp)
    assert parsed == snapshot


def test_ncp_to_model_2(switching_modes_ncp, snapshot):
    parsed = NcpFile.parse(switching_modes_ncp)
    assert parsed == snapshot
