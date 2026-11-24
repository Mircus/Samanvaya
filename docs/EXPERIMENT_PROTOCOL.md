# Experimental protocol and acceptance conditions

## Reference suite

```bash
python -m pip install -e .
python benchmarks/reference_suite.py
python examples/land_community_demo.py
python -m unittest discover -s tests -v
```

The reference suite has five predeclared scenarios with expected `ALLOW`, `UNKNOWN` or `DENY` verdicts. It outputs machine-readable JSON and exits nonzero if any assertion fails. It compares **Samanvaya's action-only v0.1 policy with its new plan-level analysis**, not with any competing vendor.

The land example demonstrates:

- a legitimate individual tool action that cannot proceed because water feasibility remains unestablished;
- the plan-bound broker refusing the effect even though the individual mandate is valid;
- search over a *trusted* alternative catalog, with a least-cost admissible proposal and a scoped minimality claim;
- an operator explicitly choosing the alternative and binding it to the broker;
- a new harmless simulated action and an audit record, without real network or purchase effects.

## Proposed third-party comparison

The non-duplication study in `DIFFERENTIATOR_AND_NON_DUPLICATION.md` defines six adversarial cases. Run them using authentic upstream systems and pinned versions. Mark each capability as built-in, configurable via policy, or new code. Do **not** label a framework incapable simply because the provided example does not exercise it.

## Formal scope of the minimality result

For trusted slots `S`, finite alternatives `E_s`, and nonnegative declared change costs, consider product space

`C = ∏_{s∈S} ({unchanged} ∪ E_s)`.

Samanvaya evaluates each candidate's whole-plan coherence and selects the least-cost admissible one(s) by uniform-cost enumeration.

If all `|C|` candidates are explored, and at least one is admissible, `minimal_proven_within_catalog` is true. It means **no less-cost candidate exists within this supplied catalog and the frozen facts / constitution / evaluator state used in that run**. It does not mean the global minimum exists among all conceivable repairs. If `max_variants` limits the search, the proof flag is false even if an admissible candidate is found.

Trust caveat: the catalog is a set of *operator-authorized possible proposals*. A model must not smuggle an action into it or silently accept the winning proposal. Selecting a candidate for actual execution requires the host to bind, verify and authorize it again.

## Acceptance thresholds for next development milestone

- Actual LangChain integration job green with the pinned v1 API, tool executed only on `ALLOW`, never on block.
- At least 20 additional adversarial tests covering identity spoofing, fake evidence, parameter alteration, concurrency, stale fact updates and human review replay.
- A real external-enforcement prototype where the agent process cannot access credentials except through a governed broker.
- Reproducible evaluation against at least two existing products, with configuration parity and evidence of capability gaps.
- Explicit performance and maintenance budget; prefer deleting code when a mature component already provides a needed function.
