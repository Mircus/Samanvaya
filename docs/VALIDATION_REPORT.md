# Validation report — Samanvaya v0.2 local baseline

**Date:** 24 November 2026. **Status:** local validation only; GitHub CI has not yet executed the new commit.

## Executed locally

- `python -m pip install -e . --no-build-isolation --no-deps`: successful editable install.
- `python -m compileall -q src tests examples benchmarks`: successful compilation.
- `python -m unittest discover -s tests -q`: **44 collected**, **42 passed**, **2 skipped** (`test_langchain_real`, dependency not installed).
- `python -m pytest -q`: compatible with unittest-discovered suite; tests pass with two skips.
- `python examples/land_community_demo.py`: individual `ALLOW`, whole plan `UNKNOWN`, no blocked effect, one permitted least-cost repair, benign simulated execution after selection.
- `python benchmarks/reference_suite.py`: **5/5 expected cases matched**; baseline comparison uses Samanvaya's own action-only policy.
- `python -m samanvaya demo --audit /tmp/samanvaya-v02-demo.jsonl`: works.
- `python -m samanvaya verify-audit /tmp/samanvaya-v02-demo.jsonl`: works, valid chain.
- `git diff --check`: clean.

## Not yet verified

- Actual imported LangChain + `create_agent` / `ToolNode` execution in a dependency-installed environment. The *real* integration tests exist but are skipped locally; CI `langchain-live` job requires this dependency and fails rather than silently skip when missing.
- End-to-end isolated service with credentials inaccessible to an adversarial agent.
- Real authenticated mandate/evidence verification and durable cross-process state consistency.
- Benchmarks against external products, including AGT/ACS, OPA, Cedar or AGP.
- Distributed collective governance and irreversible side effects.

## Interpretation

Tests support only the implemented **research prototype** behavior. They do not show that Samanvaya is original relative to all prior tools, safe for actual spending, or non-bypassable in an arbitrary host. A successful GitHub CI run is the next evidence level for LangChain compatibility.
