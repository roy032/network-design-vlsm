"""Command line interface: ``vlsmkit {plan,build,check,ping,routes}``."""

from __future__ import annotations

import argparse
import difflib
import sys
from collections.abc import Sequence
from ipaddress import IPv4Address
from pathlib import Path

from vlsmkit import __version__, ios
from vlsmkit.allocator import SubnetRequest, allocate
from vlsmkit.report import addressing_markdown, plan_json, plan_table, vlsm_tree
from vlsmkit.routing import build_routing_tables, ping, reachability_matrix
from vlsmkit.spec import Network, SpecError, load

DEFAULT_SPEC = "network.toml"


def generated_files(network: Network, root: Path) -> dict[Path, str]:
    """Every file ``build`` writes, mapped to its expected content."""
    files = {root / "configs" / f"{r.hostname}.ios": ios.render(r) for r in network.routers}
    allocs = [s.allocation for s in network.subnets]
    files[root / "docs" / "generated" / "DESIGN.md"] = addressing_markdown(network)
    files[root / "docs" / "generated" / "plan.json"] = plan_json(
        sorted(allocs, key=lambda a: a.network)
    )
    return files


def _parse_request(text: str) -> SubnetRequest:
    name, sep, hosts = text.rpartition("=")
    if not sep or not hosts.isdigit():
        raise argparse.ArgumentTypeError(f"expected NAME=HOSTS, got '{text}'")
    return SubnetRequest(name, int(hosts))


def cmd_plan(args: argparse.Namespace) -> int:
    allocs = allocate(args.supernet, args.requests)
    if args.format == "json":
        print(plan_json(allocs), end="")
    elif args.format == "tree":
        print(vlsm_tree(allocs))
    else:
        print(plan_table(allocs))
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    network = load(args.spec)
    for path, content in generated_files(network, Path(args.out)).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    network = load(args.spec)
    ok = True
    for path, expected in generated_files(network, Path(args.out)).items():
        actual = path.read_text(encoding="utf-8") if path.exists() else ""
        if actual != expected:
            ok = False
            print(f"STALE {path}")
            sys.stdout.writelines(
                difflib.unified_diff(
                    actual.splitlines(keepends=True),
                    expected.splitlines(keepends=True),
                    fromfile=f"{path} (committed)",
                    tofile=f"{path} (expected)",
                    n=1,
                )
            )
    lans = {s.id for s in network.lans}
    for (a, b), (req, rep) in reachability_matrix(network).items():
        if a in lans and b in lans and not (req.ok and rep.ok):
            ok = False
            print(f"UNREACHABLE {a} -> {b}: {req} | {rep}")
    print(
        "OK: generated files are current and all LANs are reachable"
        if ok
        else "FAILED: run `vlsmkit build` and commit, or fix network.toml"
    )
    return 0 if ok else 1


def cmd_ping(args: argparse.Namespace) -> int:
    network = load(args.spec)
    request, reply = ping(network, IPv4Address(args.source), IPv4Address(args.destination))
    print(f"request: {request}\nreply:   {reply}")
    return 0 if request.ok and reply.ok else 1


def cmd_routes(args: argparse.Namespace) -> int:
    network = load(args.spec)
    tables = build_routing_tables(network)
    if args.router not in tables:
        print(f"unknown router {args.router}; choose from {', '.join(tables)}", file=sys.stderr)
        return 2
    print("\n".join(str(r) for r in tables[args.router]))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vlsmkit", description="VLSM planner, IOS config generator and routing verifier."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("plan", help="allocate subnets for NAME=HOSTS requests")
    p.add_argument("supernet", help="parent network, e.g. 10.0.0.0/8")
    p.add_argument("requests", nargs="+", type=_parse_request, metavar="NAME=HOSTS")
    p.add_argument("--format", choices=["table", "json", "tree"], default="table")
    p.set_defaults(func=cmd_plan)

    for name, func, help_text in [
        ("build", cmd_build, "generate configs and docs from the spec"),
        ("check", cmd_check, "fail if generated files are stale or LANs are unreachable"),
    ]:
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--spec", default=DEFAULT_SPEC)
        p.add_argument("--out", default=".", help="repository root to write into")
        p.set_defaults(func=func)

    p = sub.add_parser("ping", help="simulate a round-trip ping between two addresses")
    p.add_argument("source")
    p.add_argument("destination")
    p.add_argument("--spec", default=DEFAULT_SPEC)
    p.set_defaults(func=cmd_ping)

    p = sub.add_parser("routes", help="show a router's simulated routing table")
    p.add_argument("router")
    p.add_argument("--spec", default=DEFAULT_SPEC)
    p.set_defaults(func=cmd_routes)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except SpecError as exc:
        print(exc, file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
