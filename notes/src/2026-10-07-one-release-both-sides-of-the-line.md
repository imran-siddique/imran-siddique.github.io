---
title: One release, both sides of the line
date: 2026-10-07
standfirst: AAP 0.5 deprecated a claim because a verifier may ignore it, wrote a security section saying such a claim is not a constraint, and in the same release added session_label, which a verifier may ignore. Filed as issue 33.
tags: [agent-security, standards, authorization]
sources:
  - label: opena2a-standards/agent-authorization-protocol issue 33, filed 7 October 2026
    url: https://github.com/opena2a-standards/agent-authorization-protocol/issues/33
  - label: AAP-SPEC.md 0.5.1-draft at commit 179f705
    url: https://github.com/opena2a-standards/agent-authorization-protocol/blob/179f705/AAP-SPEC.md
  - label: AAP-BROKER-PROFILE.md 0.4.1-draft at commit 179f705
    url: https://github.com/opena2a-standards/agent-authorization-protocol/blob/179f705/AAP-BROKER-PROFILE.md
  - label: CHANGELOG.md, the 0.5 entry
    url: https://github.com/opena2a-standards/agent-authorization-protocol/blob/179f705/CHANGELOG.md
  - label: schemas/bac-claims-v1.schema.json at 179f705
    url: https://github.com/opena2a-standards/agent-authorization-protocol/blob/179f705/schemas/bac-claims-v1.schema.json
  - label: aap-conformance conformance.json
    url: https://github.com/opena2a-standards/aap-conformance/blob/main/conformance.json
---

The Agent Authorization Protocol release notes for 0.5 deprecate the `fga_constraints` claim with one line of reasoning: "A verifier still ignores it." The same release adds a security consideration, §8.7, titled "A constraint a verifier may ignore is not a constraint." It also adds `session_label` to the behavioral attestation token. A verifier may ignore that one too.

AAP is the authorization layer of the OpenA2A family. An agent asks for an abstract grant, a local broker checks the agent's credential, applies policy, performs the operation and hands back only the result. No secret reaches the agent or the model behind it. The spec is at 0.5.1-draft, with an Internet-Draft revision submitted on 2 October, and the repository asks outright for review of the authorization model before it goes to a standards body. So I reviewed it.

## The rule the spec already has

Broker profile §8.3 sorts every claim into two kinds. A claim named in `aap_crit` is mandatory to understand, and a verifier that does not implement it must reject the token. Every other claim is optional to ignore, and a verifier that does not implement it must accept the token anyway.

That rule is sound, and 0.5 applies it well to the capability grant and the delegation assertion. Both carry `aap_crit`. `authorization_details` and `cnf` must be listed whenever present, because a verifier that skips `cnf` accepts a proof-of-possession token as a bearer token.

## Where it stops working

The behavioral attestation token, the BAC, has no `aap_crit`. The §6.4 claim table has 12 rows and none of them is `aap_crit`; the BAC claim schema has 13 properties and none of them is `aap_crit`. The changelog records both halves in one sentence: the grant and delegation schemas gain `authorization_details`, `aap_crit` and `cnf`, and `bac-claims-v1` gains `session_label`.

`session_label` is the session's high water mark: the union of the labels of every field the broker has admitted into the agent's context. The broker's no-write-down rule checks egress against it. So a receiver that does not implement `session_label` accepts an L3 attestation from a session that has read health records, and the label never enters its decision. §8.7 already describes the outcome, in its sentence about `fga_constraints`: "A downstream that does not understand it treats the grant as unconstrained."

## What it means for someone deploying it

Inside one broker, nothing breaks. Rule 3 of profile §6.10 checks egress against the broker's own state before the operation runs. That is enforcement, and it prevents.

The claim is evidence. It is the only way the high water mark crosses a boundary, and §6.3 has a receiver verifying a BAC against the issuing registry's key, which is exactly that crossing. The receiver is the party the claim exists for, and the party the spec leaves free to drop it.

The conformance suite is consistent with this, which is correct behaviour for an optional claim. Of 44 fixtures, 4 are BACs, 1 carries `session_label` with ACCEPT expected, and all 6 that exercise `aap_crit` are grant tokens. The suite pins itself to 0.5.0-draft.

## The issue

Issue 33 offers two ways to close it. Give the BAC `aap_crit`, with `session_label` listed whenever present; that also needs a way for a receiver to advertise claim names, since the §4.4 producer rule advertises entry types only. Or state in §6.1 that the BAC is a report and never an input to a decision, and mark the label informational. It also notes that nothing carries an accumulated label across a `peer_agent` hop, and that two schema descriptions still say "mints BACs yet", the wording the project's own status check now rejects in the Markdown, because that check does not read `schemas/`.

This is a reading of the text. I ran no broker, and the schema says no reference implementation mints BACs, so nobody is relying on this claim today.

## What did not survive checking

- The draft argued that an absent label reads as the permissive case under §4.4.2. §6.4 now separates an empty array, which means no labeled field was admitted, from an absent claim, which means the issuer holds no mark. The argument now rests on §8.7's own sentence instead.
- The first fix proposal said the §4.4 producer rule would cover it. That rule advertises entry types, not claim names, so the issue says a second mechanism is needed.
- A second finding, that §5.4 attenuation passes vacuously when a delegation omits `authorization_details`, was cut. The conformance file already calls it "a spec text gap, pending a spec sentence."

## The third time this autumn

On 8 September, the [MCP 2026-07-28 release](2026-09-08-forbade-the-swap-kept-the-signal-optional.html) forbade a silent tool-list swap and left the change signal opt-in. On 28 September, the [App Defense Alliance agent spec](2026-09-28-functional-observation-by-default.html) defaulted every untagged requirement to black-box testing, and none was tagged. Three documents, one shape: whatever the text does not mark falls to the permissive reading.

So when a spec adds a claim or a requirement, the check worth running is what a reader who skips it ends up doing. For `session_label` at 0.5.1-draft, that reader accepts the token.
