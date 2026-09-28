---
title: Functional Observation by default
date: 2026-09-28
standfirst: The App Defense Alliance AI Agent Specification defines three kinds of lab evidence and says an untagged requirement defaults to black-box testing. None of its 37 requirements is tagged, so two that need a configuration file or system logs read as black-box passes. Filed as issue 514.
tags: [agent-security, standards, evidence]
x: https://x.com/mosiddi/status/2104665046811087151
sources:
  - label: appdefensealliance/ASA-WG issue 514, filed 28 September 2026
    url: https://github.com/appdefensealliance/ASA-WG/issues/514
  - label: Comment on pull request 494, the Specification and Test Guide split
    url: https://github.com/appdefensealliance/ASA-WG/pull/494#issuecomment-5873432330
  - label: AI Agent Specification on develop, commit 97c9f94
    url: https://github.com/appdefensealliance/ASA-WG/blob/97c9f946295cedd21d533ac91910c6c4f5cc77bc/AI%20Profile/AI%20Agent%20Specification.md
  - label: AI Tool Testing Guide on develop, commit 97c9f94
    url: https://github.com/appdefensealliance/ASA-WG/blob/97c9f946295cedd21d533ac91910c6c4f5cc77bc/AI%20Profile/AI%20Tool%20Testing%20Guide.md
  - label: Pull request 427, the evidence taxonomy and the held tagging item
    url: https://github.com/appdefensealliance/ASA-WG/pull/427
  - label: Pull request 437, section 2.4.2 Verifiable Tool Identity and Provenance
    url: https://github.com/appdefensealliance/ASA-WG/pull/437
  - label: Issue 400, one source of truth for the Tool documents
    url: https://github.com/appdefensealliance/ASA-WG/issues/400
  - label: trace-spec LIMITATIONS.md, Platform state is not appraised
    url: https://github.com/agentrust-io/trace-spec/blob/e3111c7/LIMITATIONS.md
---

The App Defense Alliance AI Profile gained a good agent control on 22 September. Section 2.4.2, Verifiable Tool Identity and Provenance, merged through pull request 437. The agent may invoke only allowlisted tools with pinned identities, verifies server identity and catalog integrity when a session opens, rejects a tool definition that changes after pinning, and fails closed on anything unknown or revoked. Those are enforcement requirements on the agent, before the call, and I have no quarrel with any of them.

The same document has a sound idea about assessment too. Its Evidence Taxonomy, added in August for issue 411, sorts lab evidence into three kinds. Functional Observation is the assessor driving the production agent through its user and tool interfaces, with "No source-code or backend access." Attestation is a named artifact the developer supplies on request, and the taxonomy's example is log-file samples. Document Review covers policies that cannot be exercised.

Then one sentence sets the default: "where a requirement can be satisfied purely by exercising the running application, it is Functional Observation by default."

## The default does the tagging

On develop the three type names occur only inside the taxonomy section. A word-boundary grep of the raw file finds Functional Observation three times, Attestation three times and Document Review twice, and none of them in any of the 37 requirement Evidence blocks. So all 37 read as **Functional Observation**, including two that cannot be met that way.

Section 2.4.2's Evidence block says: *"Agent application, including its tool allowlist/registry configuration. Access to the user interface and the tool interface."* Its first test step is to review that allowlist. Neither interface exposes it. Section 5.2.1 lists "System log files", which is the taxonomy's own example of Attestation.

The 2.4.2 step also ends "(AL0/AL1 static evidence)". The document says this version "only contains testing guidance and acceptance criteria of Assurance Level 2", and leaves AL0 and AL1 to future revisions. One file over, the AI Tool Testing Guide defines both levels as evidence "based on source code inspection", the access Functional Observation rules out.

In practice, a lab report saying 2.4.2 passed does not say whether the assessor saw the allowlist, took the developer's word for it, or read a configuration file sent over the day before. Under the default, each of those is a black-box pass.

TRACE has this problem written down about itself. The trace-spec limitations file has a section headed Platform state is not appraised, and its consequence is that "a report from a machine with SMT enabled and the alias check never completed verifies exactly as cleanly as one from a machine with neither condition." An untagged Evidence block does the same to a certification one layer up. The pass is valid. What it was bought with is not in it.

## It was already proposed

The idea is not mine. Issue 411 recommended tagging each requirement. Pull request 427, which added the taxonomy and closed 411, says: "Held for WG input (not in this PR): whether to tag *every* requirement's Evidence block with a type (recommended)." Nothing tracked that item until issue 514. The AI Tool Testing Guide in the same profile already carries an evidence line on **38 of its 38** Evidence blocks, per assurance level rather than per type, so the working group has the habit on one side and not the other.

Timing matters because pull request 494, opened 22 September, splits the Agent Specification into a Specification and a Test Guide. On that branch the Test Guide holds 36 Evidence blocks and the Specification holds 16 Audit sections and none. Both files carry the taxonomy paragraph, identical to the byte, and both still say "Every AL2 test case in this specification". The branch was cut before 437 merged, so 2.4.2 is not in it yet; aeoess flagged that in review on 23 September.

## What I filed

Issue 514 asks for a type line on each Evidence block, Functional Observation unless stated, with the named artifact for every Attestation or Document Review entry, starting with 2.4.2 and 5.2.1, and for the AL0/AL1 parenthetical to go. On 494 I asked the group to name one owner for the taxonomy before merge, since issue 400 already asks for a single source of truth on the Tool side.

The counts are word-boundary greps of the raw files on develop at 97c9f94 and on the 494 head at 1be3d9e. This is a reading of the text, not an assessment I have run.

If 494 merges first, the tags go into its Test Guide: 36 blocks now, 37 once 2.4.2 is carried over.
