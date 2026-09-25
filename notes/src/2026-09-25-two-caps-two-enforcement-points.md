---
title: Two caps, two enforcement points
date: 2026-09-25
standfirst: The MCP TypeScript SDK's 1.30.1 patch added a 4 MiB body limit and a 100 message batch limit. On the Express path the SDK documents, the batch limit holds and the body limit is never consulted. A 100 kilobyte parser default refuses first, and the transport never hears about it.
tags: [agent-security, mcp, enforcement]
sources:
  - label: "@modelcontextprotocol/sdk on npm, 1.30.0 and 1.30.1 publish times"
    url: https://www.npmjs.com/package/@modelcontextprotocol/sdk
  - label: Release 1.30.1 notes, three pull requests
    url: https://github.com/modelcontextprotocol/typescript-sdk/releases/tag/1.30.1
  - label: Pull request 2717, the v1.x backport of the body and batch limits
    url: https://github.com/modelcontextprotocol/typescript-sdk/pull/2717
  - label: Issue 1354, asking for a configurable parser limit on createMcpExpressApp
    url: https://github.com/modelcontextprotocol/typescript-sdk/issues/1354
  - label: Pull request 1625, adding jsonLimit on main, merged 5 March 2026
    url: https://github.com/modelcontextprotocol/typescript-sdk/pull/1625
  - label: "@modelcontextprotocol/express on npm, 2.0.1"
    url: https://www.npmjs.com/package/@modelcontextprotocol/express
  - label: Issue 2843, non-loopback host skips Host validation
    url: https://github.com/modelcontextprotocol/typescript-sdk/issues/2843
  - label: body-parser, the json limit default
    url: https://github.com/expressjs/body-parser#limit
---

Set `maxRequestBodySize` to 20 MB on an MCP server built with the TypeScript SDK's own Express factory, send it 110 kilobytes of JSON-RPC, and it answers 413. The body of that 413 is an HTML page.

Release 1.30.1 went to npm on 23 September, two months after 1.30.0. The package diff is small: three modules changed, one added, and the version string. The added module, `requestBody`, sets two numbers. A POST body over 4 MiB gets 413. A JSON-RPC batch longer than 100 messages gets 400 with code -32600.

Both work. They are checked in different places.

## Where each one sits

The web standard transport takes a POST one of two ways. If the caller passes a pre parsed body, it uses that. Otherwise it reads the stream itself, refusing a declared Content-Length over the bound before reading anything and stopping the moment the bound is crossed. The byte cap lives inside that second branch. The batch cap sits after both branches close, so it runs on the array however it arrived.

The pull request says so. A pre parsed body *"remains the way to opt out of the SDK's read entirely"*, and the batch bound applies on both paths. Nothing is hidden. It is also the path the documented deployment takes.

## What the documented server does

`createMcpExpressApp` in the 1.x package mounts `express.json()` with no options. The Node transport's doc comment shows the handler passing `req.body` in as the pre parsed body. Express 5.2.1 resolves body-parser 2.3.0, whose limit defaults to 102,400 bytes.

I ran that server on 1.30.1 with the transport option set to 20 MB:

- 90 KB body: 200.
- 110 KB body: 413, `text/html`, from Express. The route handler ran zero times.
- 5 MiB body: the same HTML 413.
- 101 message batch: 400, code -32600, from the transport.
- The same transport reading the body itself: 110 KB passes, 5 MiB gets a JSON-RPC 413 naming 4194304 bytes.

The 20 MB setting is accepted, validated (0, -1, NaN and the string "4mb" each throw a RangeError at construction) and then **never read**. The ceiling that fires is 100 kilobytes, owned by a component the option cannot reach. On the 1.x factory nothing can reach it: its options type has two fields, `host` and `allowedHosts`.

## What the operator sees

A client gets two different 413s for one condition. One is a JSON-RPC error object. The other is an Express error page, so a client that parses errors as JSON-RPC gets HTML instead.

Monitoring splits the same way. The transport's `onerror` hook fired once for the 101 message batch and **zero times** for the 110 KB body, because the transport never ran. The only trace of that refusal is Express printing a stack to stderr through its default error handler. The parser prevented the request. The layer most teams instrument never recorded it.

## The fix exists, on the other line

Issue 1354 asked for this, and pull request 1625 added a `jsonLimit` option in March. That landed on main, which ships as the v2 split packages. `@modelcontextprotocol/express` 2.0.1, published the same day as 1.30.1, has the option, and still defaults to the parser's 100 kilobytes when it is unset.

The 1.x package is the one most people install. npm counted 40.3 million downloads of `@modelcontextprotocol/sdk` in the week to 21 September, against 239,746 for the v2 Express package. Downloads are not deployments. The gap is still two orders of magnitude.

On 1.x, skip the factory. Build the Express app with the exported `hostHeaderValidation` middleware, mount `express.json({ limit })` at the number you meant, and add an error handler that answers in JSON-RPC and logs where the rest of your refusals go. On v2, set `jsonLimit` to match `maxRequestBodySize` so the two numbers agree.

## What did not survive checking

"The factory offers no way to change the limit." True of 1.x only. v2 has had `jsonLimit` since March.

"The release reordered a Host check that is not there." Partly. 1.30.1 moved the parser below Host validation, with a shipped comment saying a disallowed Host gets 403 unread. With no `allowedHosts` and any host other than the three loopback names, that validation is not installed. Issue 2843 already reports it on main, and a second contributor confirmed it across the Express, Hono and Fastify factories on 24 September. It is their finding, so it stays there.

The release note describes two limits. On the deployment the SDK documents, one of them is 100 kilobytes and belongs to Express.
