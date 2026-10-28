"""Hand-written docs must agree with the spec (guards against doc drift)."""

from __future__ import annotations

import re

import pytest

from tests.conftest import ROOT
from vlsmkit.spec import Network

DOCS = [
    ROOT / "docs" / "VLSM_Calculation.md",
    ROOT / "docs" / "IP_Address_Table.md",
    ROOT / "README.md",
]


@pytest.mark.parametrize("doc", DOCS, ids=lambda p: p.name)
def test_documented_subnets_match_spec(network: Network, doc: object) -> None:
    text = doc.read_text(encoding="utf-8")  # type: ignore[attr-defined]
    for subnet in network.subnets:
        if subnet.name in text:
            row = next(
                line
                for line in text.splitlines()
                if subnet.name in line and str(subnet.network.network_address) in line
            )
            assert str(subnet.network.network_address) in row


def test_ip_table_rows_match_spec(network: Network) -> None:
    text = (ROOT / "docs" / "IP_Address_Table.md").read_text(encoding="utf-8")
    for router in network.routers:
        for iface in router.interfaces:
            cells = [router.hostname, re.escape(iface.short_name), str(iface.address.ip)]
            pattern = r"\|\s*" + r"\s*\|\s*".join(cells) + r"\s*\|"
            assert re.search(pattern, text), f"{router.hostname} {iface.short_name} missing/wrong"
    for host in network.hosts:
        assert re.search(rf"\|\s*{host.name}\s*\|[^\n]*\|\s*{host.address}\s*\|", text), host.name
