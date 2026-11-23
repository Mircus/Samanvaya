# Contributing

We welcome tests, adapters and reasoned architectural improvements, especially counterexamples that reveal false authorization. Read [the constitution](docs/CONSTITUTION.md), [security limitations](docs/SECURITY.md), and [ADRs](docs/adr/README.md). Keep changes small and explain what they enforce.

Before submitting changes:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m samanvaya demo --audit ./test-demo.jsonl
python -m samanvaya verify-audit ./test-demo.jsonl
```

Every change to a constitutional invariant needs positive and negative tests. Do not add test bypass knobs. Do not send personal data or API keys with traces or bug reports. For an actual security vulnerability, contact the maintainers privately.
