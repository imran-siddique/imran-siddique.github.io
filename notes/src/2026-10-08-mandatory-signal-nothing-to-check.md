---
title: The mandatory signal has nothing to check against yet
date: 2026-10-08
standfirst: AFSP v0.1 makes agent provenance mandatory, with no partial session allowed without it, and both checks it specifies for it resolve against a registry the same draft puts on the v1.0 roadmap. Issue 4 on the spec repository asks which way the working group means to resolve it.
tags: [agent-identity, standards, financial-services]
sources:
  - label: primitive-os/AFSP issue 4, filed 8 October 2026
    url: https://github.com/primitive-os/AFSP/issues/4
  - label: AFSP v0.1 Public Review Draft, 28 September 2026 (PDF, commit 0ac0df9)
    url: https://github.com/primitive-os/AFSP/blob/0ac0df9/spec/AFSP-v0.1-Public-Review-Draft.pdf
  - label: primitive-os/AFSP repository at 0ac0df9
    url: https://github.com/primitive-os/AFSP/tree/0ac0df9
  - label: LedgerDrift, What AFSP v0.1 Won't Let Your Agent Do
    url: https://www.ledgerdrift.com/opinion/afsp-what-v01-wont-let-agents-do
---

Two rows in section 6.2 of the Agentic Financial Services Protocol draft carry the agent half of the whole design. VAL-05: "Verify agent provenance attestation signature against AFSP agent registry public key." VAL-06: "Confirm agent build hash matches registry record for the agent_id." A bank runs both before an AI agent's session reaches its open banking APIs, and a failure rejects the package.

AFSP published its v0.1 Public Review Draft on 28 September, with comments open until 16 November. It covers one moment: an agent arrives at a bank on behalf of a person, and the bank has to decide whether to let it in. Five signals, bound into one signed package. S1 is the agent's own: a certified, registered, unmodified build from an accountable operator.

## The rule is as strict as the draft gets

Section 3.3 gives S1 no fallback. "A PCAA package without a valid S1 attestation SHALL be rejected." Then: "No partial session is permitted without S1." S2, the consumer's biometric consent, gets the same treatment, and section 7 specifies it in full: a TEE-held root key, a signed token, tiers and a scope envelope.

S1 gets the two rows above. Both name the AFSP agent registry, and section 16 puts that registry in AFSP-07, the Agent Provenance and Certification Registry, a v1.0 roadmap component: developer registration, build submission and hash verification, a certified build registry, and the "real-time provenance attestation API".

The draft says this about itself, more than once. Section 2 lists the agent provenance attestation format among dependencies that "will be completed through the working group before v1.0". Section 18 lists "Normative formats for the Signal 1 agent provenance attestation" as open. Section 14.2 still sets a v0.1 conformance requirement on the deferred API: responses "within 50 milliseconds at the 95th percentile". And section 7.4 says that until AFSP-07 is ratified, implementations "SHALL use the interim EKU OID guidance published by the AFSP Technical Working Group" at the repository. The repository tracks 14 files at 0ac0df9. None of them is that guidance.

## Where the commentary already is

LedgerDrift's opinion piece on v0.1 noted, in one sentence, that the AFSP-07 registry is still on the roadmap. Its larger argument is that "AFSP v0.1 builds the identity layer and stops at the edge of the authorization layer", because proving who you are uses mature tools: FIDO2, biometrics, device attestation.

That is right about the consumer. It is the agent's identity that v0.1 cannot check yet. A bank implementing the draft today can verify the person and cannot verify the software acting for them, and the draft makes the second one mandatory.

## What I filed

Issue 4 asks the working group to say which of two things is true. Section 1.5 says the AFSP Platform "operates the agent certification registry" and that "In v0.1, this role is performed by Primitive." If that registry exists today, section 3.3 should say what an S1 attestation looks like and who issues it, and the interim EKU guidance should be published. If it arrives with AFSP-07, S1 should be mandatory from the version that defines its format, and the 50 millisecond requirement belongs to AFSP-07 conformance.

It also asks for one thing beyond the version question. Section 18 lists "Agent provenance for hosted agents" as open. A build hash that matches a registry record shows a build was registered. It does not show that the process presenting the attestation is running that build, and for a cloud-hosted agent those two come apart. That deserves a place in the adversary model, not only in the further-consideration list.

## What did not survive checking

The morning brief behind this said both of the draft's defences against adversary class A1, a fraudulent agent operator, resolve to AFSP-07. Not quite. The second defence, the Authorization Scope Envelope, depends on a certificate check whose EKU values sit in AFSP-07 or the missing interim guidance, but section 7.4 also requires v0.1 implementations to enforce Tier 1 of that envelope now. It is partly live. The issue says so.

The brief also described section 3 as normative. It is "normative for the purpose of security evaluation", and the quote carries that qualifier here.

A sentence about hardware attestation and host-owning adversaries came out of the issue before filing. It rested on my own work rather than theirs, and I had not checked it to the standard of the rest.

Every quotation above was checked against a text extraction of the PDF at commit 0ac0df9, and the file count against a clone of the repository. This is a reading of the draft, not an implementation. Until the working group picks one of the two answers, an S1 verifier built from v0.1 has the rule and not the key.
