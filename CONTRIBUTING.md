# Contributing

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
make install          # pip install -e ".[dev]"
pre-commit install    # optional: ruff + design check on every commit
```

## Changing the network

1. Edit [`network.toml`](network.toml). Never edit `configs/` or `docs/generated/` by hand.
2. Run `make build` to regenerate them.
3. Run `make all`. It lints, type-checks, runs the Python and JavaScript tests and the
   design check (generated files current, every LAN reachable).
4. Commit `network.toml` together with the regenerated files.

If a change is meant to differ from the submitted Packet Tracer lab, update
`deliverables/terminal_commands.txt` as well; `tests/test_ios.py` compares the two.

## Code standards

- Python 3.11+, `mypy --strict` clean, formatted with `ruff format`.
- New behaviour needs tests; coverage below 95% fails CI.
- The JavaScript allocator in `web/vlsm.js` mirrors `src/vlsmkit/allocator.py`. Change both
  together; `web/vlsm.test.mjs` checks they agree.
