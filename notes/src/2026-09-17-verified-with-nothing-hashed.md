---
title: Verified, with nothing hashed
date: 2026-09-17
standfirst: I ran the MCP Inspector's skill verifier against a server I wrote. A skill that advertises no digests gets the same word, the same JSON and the same exit code as one whose every file hashed clean.
tags: [agent-security, mcp, evidence]
sources:
  - label: "@modelcontextprotocol/inspector on npm, 2.6.0 and 2.7.0 publish times"
    url: https://www.npmjs.com/package/@modelcontextprotocol/inspector
  - label: The CLI README's Skill verification section, where the outcome table lives
    url: https://github.com/modelcontextprotocol/inspector/blob/main/clients/cli/README.md
  - label: Inspector PR 2293, the review round that introduced the three outcomes
    url: https://github.com/modelcontextprotocol/inspector/pull/2293
  - label: SEP-2640, the Skills extension, merged 13 September 2026
    url: https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/seps/2640-skills-extension.md
---

Three runs against a stdio server I wrote, one skill served three ways, same command each time.

A manifest with a wrong digest: `mismatch`, exit 7. The same manifest with the right digest: `verified`, one file, exit 0. The checker works.

Then the third case. The skill declares `"resources": "dynamic"`, which SEP-2640 defines as generated content with no digests to publish. Stdout:

```
"conformance":[{"code":"dynamic-resources","severity":"warning",
"message":"resources is \"dynamic\": the file set is generated, so no digest
is advertised and integrity cannot be verified."}],
"frontmatter":[],"files":[],"ok":true,"outcome":"verified"
```

Stderr reads `Verified 1 skill and 0 files: no conformance errors.` Exit 0.

Integrity cannot be verified, and the outcome is verified. One JSON line, both statements.

The flag is `--verify` on the Inspector's CLI. Point it at a server and it runs SEP-2640's conformance, digest and frontmatter checks over the whole catalog and turns the answer into an exit code, which is the useful part: a server author can gate CI on it. Exit 7 is a violation, 8 is a catalog it could not finish reading.

To that CI job, the dynamic case and the fully checked case are one event. Same exit code, same `ok`, same `outcome`. What carries the difference is a file count in a line on stderr and a warning row a consumer has to go looking for by severity. A pipeline reads the exit code.

The tool's own README settles what the word is supposed to mean. Its outcome table defines `verified` and exit 0 as *"Everything was checked and everything passed."* In the dynamic report, `files` is the empty array.

It is worth being exact about what the run does. The Inspector did call `resources/read`, and my server logged serving the 129 bytes. Those bytes are parsed for the frontmatter cross check and then dropped without being hashed, because the manifest declined to say what the hash should be. So something happened. Nothing was verified.

This project has already ruled on this shape once, in its own code. `EXIT_CODES.SKILL_INCOMPLETE` exists because a read that stopped at the size bound leaves entries unfetched, and *"reporting success for a manifest whose unread entries were never fetched is a false pass."* That is a third outcome and a third exit code, invented so a job that tolerates oversized catalogs can allow 8 and still fail on 7. A catalog advertising no digests at all reaches the same false pass down a different road, and it is still filed under `verified`.

The spec has a word for the state, and it is not that one. SEP-2640 says the `"dynamic"` marker exists so a host "can tell a deliberately unverifiable skill from a malformed entry", and calls a `SKILL.md` fetched under it "unverifiable" in the same sentence where an array-backed one is "digest-verified".

Worth saying where the ceiling is even when the digest does check out. A match proves the listing and the body agree with each other. SEP-2640 states the limit in its own text: digests are unsigned and supplied by the same server that supplies the content, a match proves the two are consistent rather than that either is trustworthy, and hosts MUST NOT treat it as a security boundary. I word boundary grepped the whole 673,250 byte CLI bundle: `signature` twice, both in comments about TypeScript types. `signed`, `provenance`, `attestation`, `publisher`: zero each. Nothing in this path carries authorship.

## What did not survive checking

The brief I started from said this landed in 2.7.0, published on 16 September. It did not. I installed 2.6.0, from 9 September, and its `--verify` help text, its `dynamic-resources` message and its summary headline are the same strings. The behaviour is eight days old. What 2.7.0 actually changed on this path was the client capability declaration, the configurable catalog budget and a path-less URI fix.

I also drafted the fix as "add a third outcome value" before reading the review thread on PR 2293. There are already three. Round 15 replaced a two-state verdict with `verified`, `failed` and `incomplete` for exactly this class of reason. The ask is a fourth, and the reason it is a small ask is that the precedent is theirs.

Until something changes, the difference is readable today, and it is one field. If you gate CI on `--verify`, exit 0 does not tell you that anything was hashed. This does:

```
... --method skills/list --verify | jq -e 'select(.files | length == 0)'
```

A hit means a skill in that catalog was approved by a verifier that checked no bytes of it.
