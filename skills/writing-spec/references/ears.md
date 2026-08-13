# EARS — Easy Approach to Requirements Syntax

Deferred machinery: reach for EARS only when requirements need unusual rigor
(safety-relevant behavior, protocol conformance, contractual acceptance
criteria). For ordinary ADRs and design specs, the testable-requirement rule in
SKILL.md is enough — EARS templates make everyday software specs read stiffer
than they need to be.

EARS (Mavin et al., RE'09, developed at Rolls-Royce) constrains each
requirement to one clause order:

```
While <precondition>, when <trigger>, the <system> shall <response>.
```

Five patterns, chosen by what activates the requirement:

| Pattern | Template | Use when |
|---|---|---|
| Ubiquitous | The `<system>` shall `<response>` | Always true; no trigger |
| Event-driven | When `<trigger>`, the `<system>` shall `<response>` | Response to an event |
| State-driven | While `<state>`, the `<system>` shall `<response>` | Holds during a state |
| Optional feature | Where `<feature>` is present, the `<system>` shall `<response>` | Feature-conditional |
| Unwanted behavior | If `<condition>`, then the `<system>` shall `<response>` | Error/hazard handling |

Combine patterns when needed ("While syncing, when the peer disconnects, the
client shall persist the partial state").

Rules that carry over even without full EARS: name the system explicitly (no
passive "shall be logged" without an actor), one response per requirement, and
triggers/states must be observable — "when the user is confused" is not a
trigger.
