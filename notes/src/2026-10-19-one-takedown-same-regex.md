---
title: The MCP registry took the worm down in fifteen days. The repository field still gets a regex
date: 2026-10-19
standfirst: The takedown request against io.github.jUXTAPOSITION1/vape worked, and it is the only moderation action among 6,134 status messages. The package is still on PyPI, the check that let it through has not changed, and the registry has nearly doubled around it.
tags: [agent-security, provenance, registries]
sources:
  - label: MCP registry, the vape entry with deleted records included, read 19 October 2026
    url: https://registry.modelcontextprotocol.io/v0/servers?search=vape&include_deleted=true
  - label: Issue 1563, the takedown request, closed as completed 5 September 2026
    url: https://github.com/modelcontextprotocol/registry/issues/1563
  - label: The 21 August note this follows up
    url: https://imransiddique.com/notes/2026-08-21-repository-url-looks-like-github.html
  - label: internal/validators/utils.go, the repository URL regexes, unchanged since August
    url: https://github.com/modelcontextprotocol/registry/blob/main/internal/validators/utils.go
  - label: PR 1266, probe repository URL reachability at publish, open since May
    url: https://github.com/modelcontextprotocol/registry/pull/1266
  - label: Issue 395, validate provided repositories, last comment September 2025
    url: https://github.com/modelcontextprotocol/registry/issues/395
  - label: PyPI JSON API, vape-mcp-server, both releases not yanked
    url: https://pypi.org/pypi/vape-mcp-server/json
  - label: MCP registry API, the server list used for the counts
    url: https://registry.modelcontextprotocol.io/v0/servers
---

On 5 September the MCP registry marked every version of `io.github.jUXTAPOSITION1/vape` deleted. The status message names the malware moderation policy, the OX Security report, GitHub's block on the repository, and issue 1563, the takedown request I filed on 21 August. A maintainer closed that issue the same day with a short account of what was done and how it was verified. Fifteen days from the request, twenty-eight from publication.

That is the process working. It is also, as of today, the only time it has worked in public. I pulled every record again on 19 October, deleted ones included. There are 6,134 status messages. One describes a moderation action, and it is this one.

## What the takedown did not touch

The PyPI package `vape-mcp-server` is still installable. Both releases, 1.1.0 and 1.1.1, report `yanked: false`. A registry entry is a pointer, and removing the pointer leaves the thing it pointed at where it was.

The check that let the entry through has not changed either. `IsValidRepositoryURL` in `internal/validators/utils.go` is the same shape regex it was in August, and the only commit to that file since 1 August bumps a linter. PR 1266, which probes whether the repository is reachable at publish, is still open with review required and no comments, last updated 26 May. Issue 395, where a maintainer asked on day one for the registry to check that the publisher owns the repository, has had no comment since September 2025.

## What grew around it

For servers at their latest version, the registry went from 24,615 records in August to 46,459 now. Of those under `io.github.*` that name a GitHub repository, 676 name one owned by a different account than the publisher authenticated as, up from 498. As a share that fell, from 3.3% to 2.6%. Records with no repository at all went from 5,258 to 14,155, which is 30.5% of the registry against 21.4% in August.

So the gap the worm used is not getting worse per entry. It is getting bigger because the registry is.

## What a consumer can check today

An aggregator or a gateway that admits servers from the feed is handed the same three things a human was handed in August: a proven namespace, a proven package, and a repository URL that matched a pattern. The registry can now say "deleted under the malware policy", and that statement carries weight because a maintainer wrote it. It still carries no actor field, so a consumer reading the feed has to trust the text.

Two checks need no change on the registry side. Before admitting a server, resolve the repository URL and confirm the owner matches the namespace, which is the check issue 395 asked for. And when the registry deletes an entry for malware, look up the package it named on its own index, because the index has not necessarily heard.

## What did not survive checking

"The share of mismatched repositories held steady." I said that while reading the first counts, and it was wrong: 3.3% to 2.6%, computed against entries that name a GitHub repository.

The August-to-October comparison itself carries a caveat. The script behind the August figures was not kept, and the counts above use the latest version of each server with deleted records excluded, which is my reading of what August counted. The direction of every change survives either way; the exact growth multiple depends on that choice.

Working, the per-view counts and the status message dump are reproducible from the registry API above.
