---
title: The signature covers the question, not the answer
date: 2026-09-04
standfirst: The AI SDK signs tool approval requests with HMAC so a client cannot forge one. Whether a human said yes travels beside the signature, unsigned. I tried four ways to defeat the check and three of them were blocked.
tags: [agent-security, tool-approvals, ai-sdk]
sources:
  - label: ai 7.0.92 on npm, the published tarball this was read from
    url: https://www.npmjs.com/package/ai/v/7.0.92
  - label: AI SDK docs, Tool Approvals, Security Considerations
    url: https://ai-sdk.dev/docs/agents/tool-approvals
  - label: vercel/ai PR 15947, the 7.0.0 hardening that added the signature
    url: https://github.com/vercel/ai/pull/15947
  - label: vercel/ai PR 16068, make signed approvals mandatory, open since 12 June
    url: https://github.com/vercel/ai/pull/16068
  - label: vercel/ai issue 19313, no working private channel for a tool-approval finding
    url: https://github.com/vercel/ai/issues/19313
  - label: vercel/ai .github/SECURITY.md
    url: https://github.com/vercel/ai/blob/main/.github/SECURITY.md
---

Four ways to make a tool run without a valid human approval in the AI SDK, tried this morning
against `ai@7.0.92` with `experimental_toolApprovalSecret` configured. Mutate the arguments after
signing: blocked, invalid signature. Corrupt the signature bytes: blocked, invalid signature.
Remove the signature: blocked, missing signature. Change one boolean from `false` to `true` and
leave every other byte alone: the tool ran.

The mechanism is a human-in-the-loop gate. A tool is marked as needing approval, the model calls
it, the server stops, emits a tool approval request and waits. The approval comes back inside the
message history the client sends on the next turn. Because that history is client supplied, the
server re-checks it before executing anything.

That re-check went in at 7.0.0 on 25 June under a changelog entry labelled `fix(security)`, and the
entry names the threat plainly: a client could forge an assistant message with a pre-approved
tool-call part and have the server execute a tool with attacker-chosen arguments. Three defences
arrived with it. An HMAC signature when a secret is configured, re-validation of the tool input
against its schema, and re-resolution of the approval policy.

Now look at what the signature is computed over. In `tool-approval-signature.ts` the payload is a
JSON array of five elements: a version string, the approval id, the tool call id, the tool name,
and a digest of the input. The word `approved` does not occur in that file. I grepped it on word
boundaries. Zero.

The decision lives on a different object. `ToolApprovalRequestOutput` carries the signature, and
its doc comment says the signature binds this approval request to its tool call, which is exactly
true. `ToolApprovalResponseOutput` carries `approved: boolean` and has no signature field at all.
In `collect-tool-approvals.ts` that boolean is read straight out of the client's history and
decides which pile the approval lands in.

So the signature proves the server really asked this question, about this tool, with these
arguments. It does not prove that anybody answered.

The other two defences do not close the gap. Schema validation checks the arguments, and in this
case the arguments are untouched, which is why the mutated-input control is blocked and the
flipped boolean is not. Policy re-resolution catches a tool whose policy returns denied, but a tool
configured `user-approval` re-resolves to `user-approval`, and anything that is not denied falls
through to approved.

What makes it worth writing up is that the project's own trust-model documentation promises
otherwise. Under Security Considerations it says a client crafting a valid-looking approval "can
bypass the human-in-the-loop step", and prescribes the secret for tools that modify data or spend
money. The next section says a forged or tampered approval "is rejected before the tool executes".
Four lines further down the same page is precise: "The signature binds the approval to the exact
tool name, tool call ID, and input arguments." The precise sentence is the accurate one.

## What did not survive checking

The legacy newline-joined signature fallback looked like a re-tupling hole and is not one. The
guard tests the presented fields for newlines, and a newline-free four-field tuple joined with
newlines has exactly three newlines, so it parses uniquely. Cut.

The automatically denied case was going to be the clearest illustration, since a tool denied by
server policy is emitted as a signed request plus an unsigned `approved: false`. Weakened, because
policy re-resolution re-runs the same policy and denies it again. The live case is the
`user-approval` one.

The doc comment ending "preventing client-forged approvals" appears three times, not twice.
`stream-text.ts`, `generate-text.ts` and `tool-loop-agent-settings.ts`.

I could not check prior art at all until this morning, so I pulled every issue and pull request in
the repository mentioning approvals, HMAC or human-in-the-loop, 325 of them with their comments,
and grepped the lot. Nobody has raised this. The nearest thing is an open draft from a maintainer,
#16068, which makes signing mandatory precisely so that a client cannot forge "both sides of the
approval". It has no comments and has been open since 12 June.

Which leaves the part I have not settled, which is how to tell them. `SECURITY.md` names the Vercel
Open Source HackerOne program and nothing else. GitHub private vulnerability reporting on the
repository returns `{"enabled": false}` today. In August somebody holding a finding in this same
file opened issue #19313 to ask for a channel, because HackerOne had rejected their identity
verification. A maintainer took it seriously and tried to help. On 27 August the reporter was still
locked out for thirty days.
