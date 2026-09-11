---
title: The authentication fix that changed no authentication
date: 2026-09-11
standfirst: CVE-2026-86121 is filed as missing authentication in a computer-use agent sandbox, critical, fixed in 0.3.42. The release named as the fix changes which interface the server listens on. Its authentication path is byte-identical to the version before it, and the same allow-all branch shipped again yesterday.
tags: [agent-security, cve, computer-use]
sources:
  - label: CVE-2026-86121, CVE Program record, VulnCheck as assigner
    url: https://cveawg.mitre.org/api/cve/CVE-2026-86121
  - label: NVD entry for CVE-2026-86121, CVSS 3.1 9.8, status Received
    url: https://nvd.nist.gov/vuln/detail/CVE-2026-86121
  - label: trycua/cua issue 1892, the original report of 13 June 2026
    url: https://github.com/trycua/cua/issues/1892
  - label: trycua/cua PR 1845, fix(computer-server) default to localhost binding, four files
    url: https://github.com/trycua/cua/pull/1845
  - label: GHSA-pccw-h89v-h9cj, unreviewed, empty affected-package block
    url: https://github.com/advisories/GHSA-pccw-h89v-h9cj
  - label: OSV record for CVE-2026-86121, GIT range only, no PyPI package
    url: https://api.osv.dev/v1/vulns/CVE-2026-86121
  - label: cua-computer-server on PyPI, 76 releases, 0.3.46 published 10 September 2026
    url: https://pypi.org/project/cua-computer-server/
---

The advisory reads simply enough. CVE-2026-86121, assigned by VulnCheck and published on 5 September, says cua-computer-server skips authentication when the `CONTAINER_NAME` environment variable is unset, binds to every interface, and hands an unauthenticated caller shell commands, arbitrary file read and write, and an interactive PTY. It is classed CWE-306, Missing Authentication for Critical Function, at CVSS 3.1 9.8. Everything below 0.3.42 is affected. So you upgrade past 0.3.42 and you are done.

I pulled eight source distributions off PyPI and diffed them.

Between 0.3.41 and 0.3.42, eight files differ: package metadata, the README, a generated protobuf stub, two test files, the CLI module and the server module. The authentication code lives in `computer_server/main.py`. That file has the same MD5 in both releases, `c124c604`. Nothing in it moved.

The change is two default values. `--host` goes from `0.0.0.0` to `127.0.0.1` in the CLI, and the `Server` constructor takes the same flip. The pull request that made it, #1845, is titled "fix(computer-server): default to localhost binding" and touches four files: a changelog entry, the README, `cli.py` and `server.py`. It contains no authentication code because it was never about authentication. The listener moved to loopback. That is the whole patch, and the CVE's own reference list labels it accurately: "Bind default changed to 127.0.0.1".

Now the gate, in 0.3.46, published on 10 September, at `main.py` line 498:

```
# If no CONTAINER_NAME is set, always allow access (local development)
if not self.container_name:
    logger.info(
        "No CONTAINER_NAME set in environment. Allowing access (local development mode)"
    )
    return True
```

The same test is repeated at the HTTP, WebSocket and PTY entry points, and every one of them takes that road.

So one clause of the advisory was answered and the other was not. Binding to loopback decides who can reach the service. It does not decide whether an arriving request is allowed. Only one of those layers moved, and the one that did not is the one the advisory's title names.

This matters because of where a version number travels. Scanners and inventories consume the boundary and nothing else: below 0.3.42 vulnerable, at or above it fixed. A host on 0.3.46 reads clean, and its authentication behaviour is what it was in the spring.

And the default that did move is a default, not a constraint. The new help text tells you how to undo it: use `0.0.0.0` for external access. Anyone running this sandbox on a VM so an agent can drive it will pass that flag, because that is the point of running it. The network mitigation is then gone and the gate is the only thing left.

## The boundary does not reach the tools that read boundaries

That was the argument I expected to make. Checking it produced a second one.

The GitHub advisory for this CVE, GHSA-pccw-h89v-h9cj, is marked `unreviewed` and its affected-package block is empty. The OSV record exists but carries no package at all: its only range is a GIT range over the monorepo, with 655 release tags listed and no PyPI entry. PyPI's own vulnerability field for 0.3.41 is an empty list.

The practical result, measured rather than inferred. `pip-audit` on a pinned `cua-computer-server==0.3.41`, the version everyone agrees is vulnerable, resolves 110 packages, flags protobuf, fastmcp and diskcache, and reports zero vulnerabilities for cua-computer-server. The CNA record carries the correct package URL, `pkg:pypi/cua-computer-server`. It was dropped somewhere between the record and the ecosystem databases.

## The maintainers documented this, and so did the reporter

The allow-all path is deliberate and documented. A shipped test file calls it backwards compatibility: when neither variable is set, "the server continues to operate in local development mode (no auth required, requests succeed)". There is a flag, `UNAVAILABLE_WITHOUT_CONTAINER_NAME`, that makes the server refuse instead, answering 503. It has existed since 0.3.35 in April, two months before the report, and it is off by default.

The reporter knew. George Chen's issue names that flag in its summary paragraph. The issue, #1892, is still open, with zero comments, unchanged since 13 June.

## What did not survive checking

I thought the CVE's patch reference pointed at a commit containing no server code. It does not. Commit `59cf25c0ec54` is the lint-baseline PR #1846, merged eighteen seconds after #1845, and it carries #1845's changes among its sixteen files. The reference is correct.

I also thought 0.3.42's dependency re-pin, fastmcp from `>=2.0,<3` to `>=3.2.0,<3.3.0`, might be quiet security content, since 3.2.0 is the fix version for two fastmcp advisories. Those advisories were published on 13 July, three weeks after 0.3.42 shipped. Coincidence, not a fix.

A project is entitled to a local development mode. What a project cannot control is how a version range is read once it becomes a CVE, and this one is being read two ways at once: as an authentication fix that contains no authentication change, and as a boundary that the ecosystem databases never learned to apply.
