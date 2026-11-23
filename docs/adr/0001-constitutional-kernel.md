# ADR-0001: Separate constitutional kernel from agent execution

- **Date:** 2026-11-23
- **Status:** Accepted for baseline

## Decision

Create a small, framework-neutral Python kernel to decide whether a proposed effect is admissible. The host retains the graph runner, LLMs, tools and user interface. Samanvaya owns typed intents, bounded mandates, evidence conditions, decision results and accountability traces.

## Reasons

HUAP has valuable trace-first instrumentation but is not a comprehensive constitutional authorization system. Recreating its entire agent runtime would duplicate HYRI and third-party orchestration. A policy embedded only in prompts or after-the-fact reports would be too easy to bypass.

## Consequences

A host adapter must route every effect through the kernel. The experimental demo does not yet enforce this boundary outside cooperating callers. Host-specific broker integration is a P0 requirement.
