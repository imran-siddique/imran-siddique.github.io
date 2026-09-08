---
title: The release forbade the swap and left the signal opt-in
date: 2026-09-08
standfirst: MCP 2026-07-28 made it a protocol violation for a server to change its tool list as a side effect of what you just did. The same release forbade the server from telling you the list changed unless you subscribed, and neither official SDK subscribes by default.
tags: [mcp, agent-security, spec-review]
x: https://x.com/mosiddi/status/2097427875075096940
sources:
  - label: MCP 2026-07-28, server/tools.mdx, the new MUST NOT and the six client SHOULD bullets
    url: https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/server/tools.mdx
  - label: MCP 2026-07-28, basic/patterns/subscriptions.mdx, the opt-in rule
    url: https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/basic/patterns/subscriptions.mdx
  - label: MCP 2026-07-28, basic/patterns/mrtr.mdx, the requestState integrity requirement
    url: https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/basic/patterns/mrtr.mdx
  - label: MCP 2026-07-28 changelog, SEP-2567 and SEP-2575
    url: https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/changelog.mdx
  - label: SEP-3140, Signed Capability Declarations and Trustworthy Trust Labels, open since 27 July
    url: https://github.com/modelcontextprotocol/modelcontextprotocol/pull/3140
  - label: TypeScript SDK, packages/client/src/client/client.ts, the auto-open gate
    url: https://github.com/modelcontextprotocol/typescript-sdk/blob/main/packages/client/src/client/client.ts
  - label: Python SDK, src/mcp/client/client.py, listen() and its defaults
    url: https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/client/client.py
  - label: Issue 3207 (MCP-2026-008) and issue 3213, the cacheScope public reports
    url: https://github.com/modelcontextprotocol/modelcontextprotocol/issues/3213
---

The Model Context Protocol release of 28 July 2026 added a sentence to the tools page that reads like a security fix, because it is one:

> This set **MAY** be empty and **MAY** change over time [...] but **MUST NOT** vary per-connection or as a side effect of other requests on the connection.

That clause is new. I grepped the 2025-11-25 and 2025-06-18 tools pages for `per-connection` and `side effect of other requests`: zero hits in either, and no equivalent paragraph. It arrived with SEP-2567, which removed protocol-level sessions, and appears verbatim on the prompts and resources pages too.

Read it as a security property and it is a good one. A server that offers a few harmless tools, waits until you have used them, and then serves a different list is doing exactly what that sentence forbids.

## The signal it would take to notice

The same release, on the subscriptions page: "The server **MUST NOT** send notification types the client has not explicitly requested." That came with SEP-2575, which replaced the HTTP GET endpoint and the resource subscribe calls with one opt-in stream.

The only push signal that a tool list changed is `notifications/tools/list_changed`, and the schema says what that now means: it "is only delivered on a `subscriptions/listen` stream when the client requested it via the `toolsListChanged` filter field". A server that never sends it to an unsubscribed client is not cutting a corner. It is conforming.

So the question is what real clients do by default, and both official SDKs answer it in one file each. The TypeScript SDK auto-opens the stream, but the block is gated on `if (this._listChangedConfig)`, assigned in exactly one place: the constructor's `options.listChanged`, with no default. In the Python SDK, `listen()` is a method you call, and its filter starts at `tools_list_changed: bool = False`.

**The default in both is not subscribed.** A client built that way can still notice a change by refetching `tools/list` and diffing it. That is evidence rather than judgment, and it is the only route left, because the two freshness cues the spec does give it are both set by the party the rule constrains. `ttlMs` is server-supplied, servers **MUST** provide a value, and clients **SHOULD** assume 0 when it is absent. The notification invalidates the cache, and only reaches a client that asked for it.

## The same release knows how to write this requirement

Multi Round-Trip Requests, new in 2026-07-28, has the server hand the client an opaque `requestState` and take it back on a retry. The spec's instruction there is not a logging bullet:

> servers **MUST** treat `requestState` as an attacker-controlled input. If `requestState` influences authorization, resource access, or business logic, servers **MUST** protect its integrity (e.g. HMAC or AEAD) and **MUST** reject state that fails verification.

It goes on to require principal binding, a TTL and a digest of the originating request, to stop replay.

That is one direction. In the other direction, the one the new MUST NOT actually governs, the tools page offers six client SHOULD bullets, and the closest to the point is "Log tool usage for audit purposes". A log tells you afterwards which tool ran. It cannot decline a tool whose description changed while you were not subscribed to hear that it had. The page also tells clients to treat annotations as untrusted "unless they come from trusted servers", which is a property of the identity, not of the bytes this particular response carried.

## What is unmade, and what is not

Most of this argument is already open. SEP-3140, Signed Capability Declarations and Trustworthy Trust Labels, has been on the repository since 27 July, the day before the release. It proposes a signed manifest over the `tools/list` outputs, with change semantics for rug pulls. Its author established the need in July and I am not restating it.

What has not been said is that the release changed the case for it. SEP-3140 was drafted against the previous wire model: across its body and all fifteen comments, `subscriptions/listen`, `subscribe` and `opt-in` appear zero times, and it cites the 2025-11-25 security page. Its threat model describes a server that "emits `notifications/tools/list_changed` and silently swaps in malicious definitions", which is the behaviour the new release forbids toward a client that never subscribed. The attack it defends against got quieter on 28 July. That is the thing worth adding to the review, and it is the argument for pairing SEP-2567, which wrote the rule, with SEP-2575, which made the signal conditional, and SEP-3140, which would supply the check.

Three things I had wrong going in. An absence claim covering `integrity`, `signature` and `attest` across four spec pages was false: `attestation` appears once, in `basic/authorization/security-considerations.mdx`, on localhost redirect URIs. The tools page carries six client SHOULD bullets, not five. And the 2 September activity on SEP-3140 is a cross-reference in the timeline, not a comment; the last comment is 26 August, by the author. Following that cross-reference killed my second story, a scope-filtered tool list labelled `cacheScope: "public"`: issue 3207 reported it as MCP-2026-008 on 7 August, and issue 3213 extends it.

The check a team can run today is small. Grep your client for `subscriptions/listen`. If it is not there, you are on refetch-and-diff, and you should know that rather than discover it.
