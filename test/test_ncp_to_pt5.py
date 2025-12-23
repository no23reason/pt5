from pt5_handler.ncp_model import NcpFile
from pt5_handler.ncp_to_pt5 import ncp_to_pt5


def test_ncp_to_pt5(simple_ncp, snapshot):
    ncp = NcpFile.parse(simple_ncp)
    pt5 = ncp_to_pt5(ncp)
    assert pt5 == snapshot
