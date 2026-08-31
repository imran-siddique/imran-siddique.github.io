---
title: Two normative sentences went missing when one tasks spec superseded another
date: 2026-08-31
standfirst: The MCP tasks extension requires an authorization check on every task request. Its own rationale says that check is often impossible, the sentence that used to make servers disclose that is gone, and no error code represents a denial. One of the two losses was already found and fixed by somebody else three weeks ago.
tags: [mcp, agent-security, spec-review]
sources:
  - label: SEP-2663 Tasks Extension, merged 15 May 2026
    url: https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/seps/2663-tasks-extension.md
  - label: ext-tasks specification/draft/tasks.md, Security Considerations and Protocol Errors
    url: https://github.com/modelcontextprotocol/ext-tasks/blob/main/specification/draft/tasks.md
  - label: ext-tasks PR 9, restore auth binding requirement dropped during SEP-2663 port
    url: https://github.com/modelcontextprotocol/ext-tasks/pull/9
  - label: SEP-1686 tasks proposal, section 8.1 Task Isolation and Access Control
    url: https://github.com/modelcontextprotocol/agents-wg/blob/main/proposals/1686-tasks.md
  - label: Agents WG meeting notes, 28 August 2026, error contracts for agent operations
    url: https://github.com/modelcontextprotocol/agents-wg/blob/main/meetings/2026-08-28.md
  - label: ext-tasks schema/draft/schema.ts, Task interface and ttlMs
    url: https://github.com/modelcontextprotocol/ext-tasks/blob/main/schema/draft/schema.ts
  - label: MCP roadmap, 22 August 2026
    url: https://blog.modelcontextprotocol.io/posts/mcp-roadmap/
  - label: ext-tasks issue 20, filed 31 August 2026
    url: https://github.com/modelcontextprotocol/ext-tasks/issues/20
---

The MCP tasks extension defines three protocol error codes. `-32602` for an invalid or nonexistent task ID, `-32603` for internal errors, `-32021` for a missing client capability. Its Security Considerations require servers to perform an authorization check on every task-related request. None of the three codes represents that check failing.

So a server that runs the mandated check and denies has nothing to return that says it denied. It returns `-32602`, which is also the answer for a task that never existed. A denial and a typo are the same response.

That may be deliberate. There is a decent anti-enumeration argument for it, and the extension has no `tasks/list` for related reasons. But it is written down nowhere, so nobody implementing to the spec can tell a design decision from a hole.

I filed that and one other point as issue 20 this afternoon. Checking whether they were already raised is most of what follows, and it changed what I filed.

## The part that took reading two repositories

The requirement and its rationale do not live in the same document.

The Security Considerations bullet is in `ext-tasks`, the extension's own repo. The paragraph explaining when it can actually be satisfied is in SEP-2663, in the main specification repo, and says this:

> all tasks should be bound to some sort of "authorization context," the implementation of which is left to individual servers according to their existing bespoke permission models. However, in many cases, it is not possible to perform this binding, in which case the task ID becomes the only line of defense against contamination.

With sessions removed from the protocol by SEP-2567, there is, in the SEP's words, "no other natural scope a server can define unilaterally". `grep -ci motivation` on the ext-tasks specification returns zero. An implementer working from the extension repo sees a MUST with none of the context that bounds it.

In those deployments the mandated check reduces to the bearer check the neighbouring bullet permits, where a server MAY use task IDs as bearer tokens. Possession of the handle becomes the authorization. That is a different property from the one the MUST describes, and the document uses the vocabulary of the stronger one.

## Somebody already found half of this

The auth binding bullet was not in the extension at all until eleven days ago.

Rich Smith opened PR 9 on 31 July, titled "restore auth binding requirement dropped during SEP-2663 port". It was merged on 20 August. His argument: the port carried three of the four Security Implications bullets and dropped the second, leaving `tasks/get`, `tasks/update` and `tasks/cancel` with no specified authorization requirement. In his words, an unguessable task ID was the only control the specification mandated.

He was right and it is fixed. I did not expect the second loss underneath it.

SEP-1686, the tasks proposal this extension supersedes, had a rule for exactly the case the Motivation paragraph describes:

> Receivers that do not implement session or authentication binding SHOULD document this limitation clearly, as task results may be accessible to any requestor that can guess the task ID.

That sentence is not in SEP-2663 and not in the extension. The requirement to bind survived the transition, after being restored by hand. The requirement to disclose when you cannot bind did not survive, and nobody has restored it.

Two normative sentences from the same section went missing in the same supersession. One was caught by a contributor doing a bullet-by-bullet diff. The other is still gone.

## What did not survive checking

The framing I started with was that the document contradicts itself. It does not, because the two halves are in different repositories, and on the repo where the requirement lives the rationale is simply absent. That is a weaker claim and a more useful one: this is a porting loss, not a drafting error, and it has the same signature as the one already fixed.

I also could not claim the error taxonomy point was novel. The same shape was raised during SEP-2663 review for `requestState` integrity failures, and the maintainers resolved it on 4 May by allowing a synchronous error path as SHOULD statements. That is why two lines in Protocol Errors read SHOULD today. The authorization case is the one that conversation did not cover.

And the Agents WG settled the governing principle three days ago, on 28 August, for a different proposal: operation-specific error codes should be defined, reusing an existing protocol code where an appropriate one exists. Pointing at a decision a group has already made is worth more than arriving with an argument they have not asked for.

## The check worth stealing

When a specification says it supersedes another, diff the security sections rather than reading the new one. Two separate losses came out of one transition here, and the one that was caught was caught by somebody comparing bullets by hand.

The roadmap published on 22 August wants servers recognising agent identities built on existing standards "rather than pasted API keys and long-lived tokens", and names maturing this extension so it can move into the core specification. In the draft schema `ttlMs` is `number | null`, null documented as unlimited. A handle that may be a bearer token and need never expire is worth reconciling with that sentence while the document is cheap to change.
