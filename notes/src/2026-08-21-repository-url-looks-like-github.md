---
title: The MCP registry checks that the repository URL looks like GitHub
date: 2026-08-21
standfirst: Publishing proves you own the namespace and you own the package. The repository URL next to them gets a regex, 498 entries name a repo owned by someone other than the publisher, and the one a vendor flagged twelve days ago is still marked active.
tags: [agent-security, provenance, registries]
x: https://x.com/mosiddi/status/2090860776785645777
sources:
  - label: MCP registry, the io.github.jUXTAPOSITION1/vape entry, read 21 August 2026
    url: https://registry.modelcontextprotocol.io/v0/servers?search=vape
  - label: Official registry requirements, the four validations enforced on publish
    url: https://github.com/modelcontextprotocol/registry/blob/main/docs/reference/server-json/official-registry-requirements.md
  - label: internal/validators/validators.go, validateRepository
    url: https://github.com/modelcontextprotocol/registry/blob/main/internal/validators/validators.go
  - label: internal/validators/utils.go, IsValidRepositoryURL and the two regexes
    url: https://github.com/modelcontextprotocol/registry/blob/main/internal/validators/utils.go
  - label: Official registry API reference, status values and the statusMessage restriction
    url: https://github.com/modelcontextprotocol/registry/blob/main/docs/reference/api/official-registry-api.md
  - label: The MCP Registry moderation policy
    url: https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/moderation-policy.mdx
  - label: Issue 395, validate provided repositories are publicly reachable, open since September 2025
    url: https://github.com/modelcontextprotocol/registry/issues/395
  - label: PR 1266, probe repository URL reachability at publish
    url: https://github.com/modelcontextprotocol/registry/pull/1266
  - label: OX Security, Shai-Hulud outbreak debrief, 9 August 2026
    url: https://www.ox.security/blog/shai-hulud-outbreak-debrief-the-worm-evolves-into-mcp/
  - label: PyPI JSON API, vape-mcp-server
    url: https://pypi.org/pypi/vape-mcp-server/json
  - label: cMCP LIMITATIONS.md, tool name collision via malicious catalog entries
    url: https://github.com/agentrust-io/cmcp/blob/main/LIMITATIONS.md
  - label: Issue 1563, the takedown request I filed against the entry
    url: https://github.com/modelcontextprotocol/registry/issues/1563
---

The official MCP registry holds 24,615 server records. Of the 16,850 published under an
`io.github.*` namespace, 15,235 name a GitHub repository, and 498 of those name a repository
owned by a different GitHub account than the namespace the publisher authenticated as.

Most of those 498 are almost certainly innocent. A personal account publishing an
organisation's code, a monorepo, an account rename. That is the point. Nothing checked, so
nothing distinguishes them.

## What publishing actually proves

The requirements document is clear and short. Four validations: namespace authentication,
package ownership verification, restricted registry base URLs, and `_meta` namespace
restrictions. Grep it for "repositor" and you get nothing.

The code is not silent, though, and the difference matters. `validateRepository` calls
`IsValidRepositoryURL`, which is this:

```
^https?://(www\.)?github\.com/[\w.-]+/[\w.-]+/?$
```

A shape check. Not whether the repository exists, not whether it resolves, not whether the
publisher owns it, not whether it has anything to do with the package sitting beside it in
the same record. If the field is absent the validator returns early, which is how 5,258
entries have no repository at all.

So the record proves two things and asserts a third. The namespace is proven. The package is
proven. The repository is typed in.

None of which is news to the maintainers. Issue 395 was opened in September 2025 by someone who
found a live entry pointing at a GitHub URL that would not load, and the first reply, from a
maintainer, is that the registry should "go one step further" and validate that the repository
is "not only valid/publicly accessible but also actually owned by the publisher". Eleven months
later the thread has eight comments, the URL in question turned out to be a private repo rather
than a broken link, and PR 1266 has had a publish-time reachability probe waiting since May.
The check the maintainer asked for on day one has not been built.

## What used the gap

On 8 August at 20:58 UTC, `io.github.jUXTAPOSITION1/vape` was published. On 9 August, one day
later, OX Security reported it. Their account: the PyPI package is clean, deliberately, to get
past automated scanners, and the payload sits in the linked repository in
`.vscode/settings.json` and `.claude/settings.json`, which run when a developer opens or
clones the project in a coding client. They describe it as the first time they had observed
this worm delivered through the official registry.

Every prior version of this story ran the other way. Honest repository, poisoned package.
Here the clean package is the alibi and the pointer is the weapon, and the pointer is the
field that gets the regex.

GitHub blocked the repository for terms-of-service violation on 15 August. The PyPI package
is still installable, both releases, neither yanked. The registry entry is still `active`,
and its `statusChangedAt` is identical to the microsecond to its `publishedAt`.

## Why nobody attached a warning

There are three statuses. `active`, visible by default. `deprecated`, visible with a message.
`deleted`, hidden by default. `statusMessage` is capped at 500 characters and rejected with a
400 when the status is `active`.

I read all 735 status messages in the registry. Not one describes a moderation action. They
are renames, consolidations, accidental version bumps, republications under a new namespace.
That is not a failure, it is the feature working as designed: `statusMessage` was introduced
to carry a publisher's deprecation reason, and issue 623 was closed on exactly that ground.

Which leaves the vocabulary with no way to say the thing this entry needs said. An aggregator
mirroring the feed cannot tell a publisher's rename from a registry takedown, because both are
a status plus free text, and there is no actor on the record.

## What did not survive checking

"The registry does not validate the repository field." Cut. It validates the shape. One grep
would have refuted the stronger claim in public.

"The choice is silence or removal." Cut. `deprecated` is documented as visible with a warning.
The measured claim replaces it: the warning tier exists and has never once been used for this.

"The repository was deleted." Corrected. GitHub's API records it as blocked for terms of
service since 15 August, which is a stronger fact than the 404 I started from.

"The maintainers deferred ownership binding." Cut, and it was nearly the worst error here. That
is PR 1266's characterisation of the thread. The thread itself has a maintainer asking for
ownership validation in the first reply. Nobody decided against it.

I have not run the payload or read the repository, which is disabled. The attribution is OX
Security's and I am reporting it as theirs.

## Where I sit in this

cMCP's own limitations file says the gateway cannot detect a look-alike package added to the
catalog in the first place, because catalog approval is human-gated. This is a case study in
what that human is handed: a green status, a proven package name, and a repository URL that
was checked for punctuation.

Filed today as issue 1563, a takedown request against the entry, citing the moderation policy's
malware clause. The reachability gap is already in 395 and 1266 and does not need me to file it
again.
