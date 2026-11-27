# Validation report — Samanvaya v0.2

**Reference revision:** [`ac4265d569042d850d4a49794ea3cb775ccd9835`](https://github.com/Mircus/Samanvaya/tree/ac4265d569042d850d4a49794ea3cb775ccd9835).  
**Local baseline:** 24 November 2026. **CI evidence reviewed:** 27 November 2026.

## Executed locally (recorded 24 November)

- Editable installation with `--no-build-isolation --no-deps`: successful.
- `python -m compileall -q src tests examples benchmarks`: successful.
- `python -m unittest discover -s tests -q`: 44 collected, 42 passed, 2 skipped (`test_langchain_real`, optional dependency absent).
- `python -m pytest -q`: compatible suite with two optional skips.
- `python examples/land_community_demo.py`: individual ALLOW, whole-plan UNKNOWN, no blocked effect, permitted least-cost repair, benign simulated execution after selection.
- `python benchmarks/reference_suite.py`: 5/5 expected cases matched; baseline is Samanvaya's own action-only policy.
- CLI demonstration and audit verification: successful; valid local hash chain.
- `git diff --check`: clean.

## GitHub CI subsequently verified

[Actions run 45388976640](https://github.com/Mircus/Samanvaya/actions/runs/45388976640) on the reference revision completed successfully on 24 November.

| Job | Result |
|---|---|
| Core Python 3.11 | Passed |
| Core Python 3.12 | Passed |
| Core Python 3.13 | Passed |
| LangChain live | Passed, 2 tests |

All three core jobs successfully installed the package, ran unittest discovery, the CLI demonstration, audit verification, the land example and the internal benchmark. The separate LangChain job installed LangChain 1.5.2, langchain-core 1.8.4 and ran `SAMANVAYA_REQUIRE_LANGCHAIN=1 python -m unittest tests.test_langchain_real -v`. Both `test_agent_blocks_unregistered_tool` and `test_agent_executes_authorized_tool` passed. The tests use an actual installed framework and deterministic no-network test model, not a remote LLM. They cover narrow synchronous action-level middleware behavior, not plan-bound repair across arbitrary framework nodes.

## Still not verified

- End-to-end isolated service with credentials inaccessible to an adversarial agent.
- Real authenticated mandate/evidence verification, durable cross-process state and aggregate plan quota handling.
- Benchmarks against external products, including AGT/ACS, OPA, Cedar and AGP.
- Runtime completion witnesses for order constraints, distributed collective governance and irreversible side effects.
- The educational notebook has been structurally validated and its code syntax checked; a complete Colab execution was not performed in preparing this documentation update.

## Interpretation

The results support the implemented **research prototype** behavior and narrow installed-framework interoperability. They do not show that Samanvaya is original relative to all prior tools, safe for actual spending, or non-bypassable in an arbitrary host. No paid model calls are required for the reference demonstrations. See [SECURITY.md](SECURITY.md) and [EXPERIMENT_PROTOCOL.md](EXPERIMENT_PROTOCOL.md).
