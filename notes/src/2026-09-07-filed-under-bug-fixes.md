---
title: The fix shipped three weeks before the bug had a name
date: 2026-09-07
standfirst: One coding agent answered repo-controlled git config with a confirmation prompt in August. Another answered the neighbouring case with a refusal. The gap between those two choices is the whole argument, and neither public record tells you which one you are running.
tags: [agent-security, supply-chain, coding-agents]
x: https://x.com/mosiddi/status/2097738166488969237
sources:
  - label: Qwen Code CHANGELOG, v0.21.9 (2026-08-10), the diff.external and core.fsmonitor line, PR 8645
    url: https://raw.githubusercontent.com/QwenLM/qwen-code/main/CHANGELOG.md
  - label: Claude Code CHANGELOG, v2.1.196, the single line marked Security
    url: https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md
  - label: CVE-2026-72718, goose CLI arbitrary command execution via git core.fsmonitor, fixed 1.44.0
    url: https://api.osv.dev/v1/vulns/CVE-2026-72718
  - label: CVE-2026-71963, Hermes Agent RCE via git core.fsmonitor config injection
    url: https://api.osv.dev/v1/vulns/CVE-2026-71963
  - label: CVE-2026-33068, Claude Code workspace trust dialog bypass via repo-controlled .claude/settings.json, fixed 2.1.53
    url: https://api.osv.dev/v1/vulns/GHSA-mmgp-wc2j-qcv7
---

On 10 August, Qwen Code shipped v0.21.9. One line in its changelog, filed under Bug Fixes:

> Requires explicit confirmation for read-only Git commands when repository configuration executes external programs via `diff.external` or `core.fsmonitor`.

Three weeks later that shape of bug got a name and a list of affected coding agents.

The mechanism is not in dispute. Two CVE records describe it in the same terms. In goose, a
repository whose `.git/config` sets `core.fsmonitor` to a command causes git to run that command
during the index refresh that `git diff HEAD` performs, before the agent contacts a model at all.
In Hermes Agent, the same key fires on the `git status` refresh triggered by sending any message.
Both were fixed. Neither fix required the researchers to be clever; the repository simply supplies
part of the command line.

## Two vendors, one bug class, two different controls

Qwen's answer is a confirmation prompt. Claude Code's changelog gives the other answer, from a
neighbouring case. In v2.1.196 there is exactly one line marked Security:

> `claude mcp list`/`get` no longer spawn `.mcp.json` servers that a repo self-approved via a
> committed `.claude/settings.json`; untrusted workspaces show Pending approval

Same class. A file committed inside a repository causes the agent to spawn a process during a
command whose name suggests it only reads. `list` and `get` sound as passive as `status` and
`diff`. The control chosen is different. It does not ask the developer whether this repository
should be allowed to configure itself. It refuses, and marks the workspace pending.

That gap is the argument. A confirmation prompt asks a developer to adjudicate `core.fsmonitor` in
a repository they opened ninety seconds ago, before they have read a line of it, while the thing
they wanted was to start work. Everything needed to answer the question sits inside the artifact
the question is about. Prompts of that shape get approved, and the people most likely to approve
them are the ones who have seen the prompt before and had it be fine every previous time. A prompt
is a control that degrades with familiarity. The control that holds is the one that never asks:
run git with the repository's values for those keys unset, and the question does not arise.

## What the public record cannot tell you

Coverage credits Claude Code v2.1.196 with fixing the `core.fsmonitor` issue. Two records a
careful user would check disagree by saying nothing at all.

The changelog is silent. I grepped the published file, all 6,362 lines. `fsmonitor` does not
appear. Neither does `diff.external`, nor the string `core.` anywhere in the file.

The advisory database is also silent. goose and Hermes both have CVE records naming this exact
mechanism. For Claude Code there is no advisory published in August or September 2026, and none
listing a fixed version anywhere in the 2.1.19x range. The most recent is from 24 July.

That is not evidence that no fix shipped. Silent fixes are ordinary and often correct. It is
evidence of something narrower: from the changelog and the advisory database together, a person
running v2.1.196 cannot establish whether they have this fix, while a person running goose or
Hermes can establish it in one query. Anyone diffing changelogs to decide whether to upgrade gets
no answer, and diffing changelogs is what most teams actually do.

Worth adding that `.claude/settings.json` has been an attacker-controlled trust input before. In
March, CVE-2026-33068 described a malicious repository setting `permissions.defaultMode` to
`bypassPermissions` in that committed file, silently skipping the trust dialog. Fixed in 2.1.53.
The September line is the second time the same repo-controlled file has had to be defended against
the same idea.

## What did not survive checking

The researchers' report is not in here. Their domain, and three write-ups of it, were unreachable,
so every claim that originates with them stayed out: the name given to the disclosure, the count
of affected agents, the tally of unpatched issues, and the specific claim that Qwen Code remains
affected at v0.22.3. That last one is why this note does not tell you whether the August prompt
held. Nine stable releases separate v0.21.9 from v0.22.3, and I can see the mitigation shipped and
cannot see whether it was enough.

One figure was wrong on the way in. The single Security line in v2.1.196 is one of **nine** such
lines in that changelog, not seven; the first count matched only the unbolded form and missed two
written as `**Security:**`.

Pull request 8645 landed on 10 August. Whoever wrote it was not responding to a disclosure,
because there was not one yet. They found it, wrote one sentence, and shipped. That sentence then
sat in a public changelog, naming both configuration keys, for three weeks, while the same key was
still live in other agents. It was never hidden. It was filed under Bug Fixes.
