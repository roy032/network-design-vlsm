"""vlsmkit: VLSM planning, Cisco IOS config generation and routing verification.

The Animal Kingdom network in this repository is described once, in
``network.toml``. Everything else (addressing plan, router configs,
documentation tables and the reachability report) is derived from it.
"""

from vlsmkit.allocator import (
    Allocation,
    InsufficientAddressSpaceError,
    SubnetRequest,
    allocate,
    prefix_for_hosts,
)

__all__ = [
    "Allocation",
    "InsufficientAddressSpaceError",
    "SubnetRequest",
    "allocate",
    "prefix_for_hosts",
]

__version__ = "1.0.0"
