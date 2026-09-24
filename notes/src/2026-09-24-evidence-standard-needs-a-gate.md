---
title: The evidence standard that needs a gate to count
date: 2026-09-24
standfirst: Proof-of-Control positions itself as the evidence half of agent assurance, not runtime enforcement. Its own threshold requires an in-path gateway that withholds actions, and its threat model has no row for that gateway. Filed as issue 78.
tags: [agent-security, standards, enforcement]
sources:
  - label: LFDT-ProofOfControl/ov-poc-standard issue 78, filed 24 September 2026
    url: https://github.com/LFDT-ProofOfControl/ov-poc-standard/issues/78
  - label: LFDT-ProofOfControl/ov-poc-standard issue 79, one-pager residual trust
    url: https://github.com/LFDT-ProofOfControl/ov-poc-standard/issues/79
  - label: README, "What Proof-of-Control is NOT", commit 22c7b62
    url: https://github.com/LFDT-ProofOfControl/ov-poc-standard/blob/22c7b62/README.md
  - label: C7 Evidence Generation and Properties, 7.1.1 to 7.1.5, 7.3.2, 7.6.1 to 7.6.3
    url: https://github.com/LFDT-ProofOfControl/ov-poc-standard/blob/22c7b62/0.1/en/0x10-C07-Evidence-Generation-and-Properties.md
  - label: Using Proof-of-Control, Requirement Levels table
    url: https://github.com/LFDT-ProofOfControl/ov-poc-standard/blob/22c7b62/0.1/en/0x03-Using-Proof-of-Control.md
  - label: Appendix C, Threat Model (normative)
    url: https://github.com/LFDT-ProofOfControl/ov-poc-standard/blob/22c7b62/0.1/en/0x92-Appendix-C_Threat-Model.md
  - label: C10 Conformance and Disclosure, 10.3.2
    url: https://github.com/LFDT-ProofOfControl/ov-poc-standard/blob/22c7b62/0.1/en/0x10-C10-Conformance-and-Disclosure.md
  - label: CSA AARM crosswalk (draft seed coding)
    url: https://github.com/LFDT-ProofOfControl/ov-poc-standard/blob/22c7b62/mappings/csa-aarm.md
  - label: CISO review of v0.1.4, finding F1
    url: https://github.com/LFDT-ProofOfControl/ov-poc-standard/blob/22c7b62/docs/reviews/ciso-review-v0.1.4.md
---

"Enforcement decides what an agent may do; verification shows what it actually did."

That line is from the Proof-of-Control crosswalk against CSA AARM, and it is a good division of labour. The README repeats it as a boundary: under what Proof-of-Control is not, one of four entries is "Not runtime enforcement." I use the same split in my own work. A gate prevents. A signed record proves. A log has never stopped anything.

The standard, currently Working Draft v0.1.4 and open for public comment until 30 October, does not hold to it.

## Where the line moves

C7.1 is called Generation at the Action Boundary. Three of its requirements describe a component that holds actions back:

- 7.1.1: "the agent has no network or credential path to its tools that bypasses the gateway."
- 7.1.3: "the gateway does not forward the action to the tool until the *before* record is durably written."
- 7.1.4 (c): "an attested enforcement point that admits only requests carrying matching evidence."

All three are Level 3. The standard's Requirement Levels table says meeting every Level 1 to 3 requirement in the claimed domains is the minimum for a Proof-of-Control claim. So nothing gets the label without an in-path, fail-closed gateway. That is enforcement, at the service, before the operation runs. Its only policy is that evidence exists, but it withholds the action all the same.

I think those requirements are right. Evidencing a policy evaluation without controlling the effect channel is how a system ends up with perfect records of decisions it never enforced, and 7.1.5 caps that case below the threshold for exactly that reason. The problem is what happened around them.

## The component with no row

Appendix C is the normative threat model: 32 coverage rows. In the column describing what Proof-of-Control defends against, 12 rows use "gate" or "gates". Word-boundary matches on the raw file for gateway, intercept, interception, mediation, custody and bypass: zero for all six.

The gateway sees every action at Level 3, holds the signing keys that 7.3.2 puts out of the operator's reach, and at Level 4 refuses actions under 7.6.3 when evidence cannot be written. The CISO review found the failure case, F1, "No fail-closed requirement", and it was applied as 7.6.1 and 7.6.3. The compromise case never got a row.

The nearest row, audit tampering, is about a host rewriting the record. A compromised gateway rewrites nothing. It signs true records for the actions it lets through and writes nothing for the ones it does not, and every signature verifies.

## The check that does not reach it

Here is the part that is not in the issue, and it is the part I would test first.

At Level 4, 10.3.2 requires evidence to cover every in-scope action, "demonstrated by reconciling gateway action counts against evidence-record counts over an audit window, with zero unexplained difference." Both numbers come from the gateway. An action that goes around it adds to neither count, so the reconciliation balances.

That is judgment, not a measurement. I have read the text; I have not run a conformant deployment against it. But the arithmetic does not depend on the implementation.

## What I filed

Issue 78 asks for three things: two Appendix C rows, gateway compromise and gateway bypass, with honest coverage grades; the gateway operator added to the C10.2 trust-assumption disclosure; and a restated boundary. My suggested wording is that Proof-of-Control does not define the policy an agent is held to, and does require an enforcement point whose only policy is that evidence exists. Issue 79 is smaller: the one-pager still tells newcomers Tiers 3 and 4 require trusting "no one", a claim C8 has already withdrawn. Comments in the window get a published disposition.

For anyone evaluating a system that claims Proof-of-Control, ask who operates the gateway, then reconcile the tool side's own request logs against the evidence store rather than the gateway's counts. A tool call that appears in the first and not the second is the row Appendix C is missing.
