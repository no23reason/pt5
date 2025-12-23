from pt5_handler.ncp_model import NcpFile


def test_ncp_to_model(simple_ncp):
    parsed = NcpFile.parse(simple_ncp)
    print(parsed.commands)
    assert len(parsed.commands) == 7
