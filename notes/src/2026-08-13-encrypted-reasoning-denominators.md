---
title: What the encrypted reasoning paper actually counted
date: 2026-08-13
standfirst: Coverage of the reasoning-trace harvest reported three different totals as if they disagreed. They are all the paper's own numbers, at three different denominators.
tags: [agent-security, evidence, retention]
linkedin: https://www.linkedin.com/feed/update/urn:li:activity:7493711977589125120/
x: https://x.com/mosiddi/status/2091274249931829397
sources:
  - label: Panfilov et al., "Stealing Reasoning Traces from Proprietary LLM APIs", arXiv 2608.09867, 10 August 2026
    url: https://arxiv.org/abs/2608.09867
  - label: Matthew Green, "Let's talk about encrypted reasoning", 29 May 2026
    url: https://blog.cryptographyengineering.com/2026/05/29/fooling-around-with-encrypted-reasoning-blobs/
  - label: TRACE specification, LIMITATIONS.md
    url: https://github.com/agentrust-io/trace-spec/blob/main/LIMITATIONS.md
---

A paper posted on 10 August showed that the encrypted reasoning blocks Anthropic, OpenAI and Google hand back to API clients were interchangeable inside each provider. A block issued in one session could be replayed into a different session, a different account, a different model in the same family. Hand it to a weaker sibling model and ask it to transcribe, and it reads the contents back in plain text.

No cipher was broken. The ciphertext was confidential and it was bound to nothing.

I want to record two things that the coverage got wrong, because both are the kind of error that survives into everyone's slide deck.

## The three totals are not a disagreement

Different outlets reported the harvest as 182 credentials plus 367 pieces of personal information, or as 704 artifacts, or as 912. Read side by side those look like sources contradicting each other, and at least one write-up said so.

They are all in the paper, and they count different things:

- **912** is every privacy artifact recovered, including the ones that came from benchmark sources rather than real users.
- **704** is the subset from genuine, non-benchmark user sessions. That is the number that means something, because those are real people's secrets.
- **182 credentials and 367 pieces of personal information** are two of the paper's three artifact categories, which is what its abstract leads with.

Within the genuine-session set, the breakdown is 62 API keys, 33 passwords, 24 access tokens, 7 private keys and 30 personal email addresses. The scan covered 6,708 publicly posted agent trajectories and decoded 315,320 reasoning blocks.

The lesson is not about this paper. It is that coverage reliably repeats a number and drops the scope attached to it, and two correctly-reported numbers at different denominators then read as a contradiction. If you find yourself adjudicating between outlets, the answer is usually that nobody disagreed and the denominators were thrown away in the retelling.

## The dismissals were not a response to this paper

Matthew Green reported the replay behaviour on 29 May, three months earlier. His account of what came back is worth quoting exactly, because a shortened version of it is now circulating with the causality reversed:

> OpenAI said my report was unreproducible

> Anthropic quite reasonably told me they don't see any security implications in side channels or replays

Several summaries have welded those quotes onto the August paper, producing a story where providers waved the researchers away and the team ran the harvest to force the issue. That story is not in the paper. Its disclosure section says all model providers acknowledged receipt of its report, and it attributes the earlier dismissals to Green's May disclosure by citation. Green himself calls Anthropic's answer a fine decision.

So the honest version is duller and more interesting: a cryptographer flagged the primitive in May, the providers judged it low severity, and a paper in August measured what the primitive was costing in the wild. Nobody in that sequence behaved badly. The gap was that no one had counted.

The paper's reproducibility statement notes that as of August the results no longer reproduce, because of mitigations the providers implemented following the disclosure. It does not date those mitigations, and I have not seen anyone who can.

## The part that is mine

The missing control is a binding check at decrypt: this block was issued for this session, this account, this model, or it is refused. It runs at the provider's API boundary, because that is the only place the plaintext exists. No gateway, no agent framework and no policy layer can validate a binding on a payload it cannot open. That is enforcement, and it prevents the replay.

The evidence layer has a different job and it does not prevent anything. It decides what is allowed into the record in the first place.

Here is where that lands on my own work. The TRACE specification says, in its stated limitations:

> does not record the model's internal chain-of-thought, intermediate reasoning, or context window contents

We file that under Known Limitations and it belongs there, because reasoning that changes behaviour without producing a tool call never reaches the record. It is also the reason a TRACE record contains nothing we cannot read back, which is the property this paper makes expensive to lack. Sixty-four of the recovered artifacts appeared only inside the opaque blocks and nowhere in the visible transcript. Some developers had cleaned the readable session before publishing it and shipped the secrets anyway.

A retention policy is a claim about fields you can read. If your trace carries a field you cannot open, you do not have a retention policy for it. You have a hope.
