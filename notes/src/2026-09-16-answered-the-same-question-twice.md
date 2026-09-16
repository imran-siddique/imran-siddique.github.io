---
title: One repository answered the same question twice on 11 September
date: 2026-09-16
standfirst: Four hours apart, awslabs/mcp merged a parser-based read-only policy for one database server and twenty more regex keywords for another. I installed the published package and found the keyword answer still has a gap the parser answer cannot have.
tags: [agent-security, mcp, sql]
x: https://x.com/mosiddi/status/2100318071307309221
sources:
  - label: awslabs/mcp commit f6aec97, parser-based sql policy (#4575)
    url: https://github.com/awslabs/mcp/commit/f6aec97d0aa3b9caae0cd131dda4a63be5709f64
  - label: awslabs/mcp commit a55a1a8, statement-leading mutating verbs (#4615)
    url: https://github.com/awslabs/mcp/commit/a55a1a8da1991767e114a7039b7245992b900b4b
  - label: CVE-2026-85788, GHSA-x25m-ph3m-3r9q, mysql read-only via inline comments
    url: https://github.com/awslabs/mcp/security/advisories/GHSA-x25m-ph3m-3r9q
  - label: CVE-2026-87911, GHSA-fph8-pg5w-78fv, postgres COPY TO PROGRAM
    url: https://github.com/awslabs/mcp/security/advisories/GHSA-fph8-pg5w-78fv
  - label: AWS vulnerability reporting page, where this finding went
    url: https://aws.amazon.com/security/vulnerability-reporting/
---

On 11 September, four hours apart, the awslabs/mcp repository merged two fixes for the same class of problem, and they do not agree with each other.

At 15:31 UTC, commit f6aec97 landed a parser-based read-only policy for the Postgres server (#4575). It deletes that server's regex mutable-SQL detector and replaces it with a guard built on pglast, which is PostgreSQL's own parser compiled in. The module says why in one line: identifiers, quoting, comments and Unicode escapes can no longer disguise an operation, because *the guard and the database read the same bytes the same way.* The check for the statement behind CVE-2026-87911 is now a field on a parse-tree node, not a pattern.

At 19:22 UTC, commit a55a1a8 answered the same problem for the MySQL server (#4615) by adding roughly twenty more keywords to a regex.

Both are on main. Both are real work. Only one of them changes what kind of thing the control is.

## Why the difference is measurable

The MySQL gate already took a CVE for this, CVE-2026-85788. AWS described it exactly: the check matches SQL text with patterns that expect literal whitespace between keywords, MySQL treats a comment as whitespace, so a comment wedged between two words walked straight through. The fix strips comments before the scan. It works. I checked it.

The class is not closed, because a comment is not the only thing MySQL treats as whitespace. A second space is too.

I installed the current published package, version 1.1.2, uploaded 8 September, and called the shipped read-only gate directly. It is two functions, and nothing else stands between a tool call and the database. One space between the two words of a multi-word keyword is rejected. Two spaces, a tab or a newline between the same two words returns an empty list from the keyword scan and an empty list from the injection heuristic, which together are the server's whole rejection path. I have sent the specific statements to the AWS vulnerability reporting page, which is where the repository's own contributing guide says security findings go instead of a public issue, so they are not in this note.

The cause is one expression. The pattern is built by escaping the whole phrase, which bakes a single literal space into the middle of it. Most entries survive that because their first word is blocked on its own. `CREATE FUNCTION` is covered because `CREATE` is. A couple have no such cover.

## The repository already contains the fix

Two of the four keyword detectors in the same monorepo, for SQL Server and Oracle, build the identical pattern by splitting the phrase on spaces and joining the words with a whitespace class. I ran Oracle's detector against every multi-word keyword it has, under one space, two spaces and a newline. Blocked every time.

So the regex approach can be made whitespace-correct, and somebody in this repository already did it, in a file next door. The small fix is a two-line copy.

Worth saying: the Aurora DSQL detector uses the same escape-the-whole-phrase construction as MySQL, and gets away with it only because a second set of anchored regexes catches the same statements a different way. It is the same latent bug, one server over, currently masked. All of this is still a small fix to a text filter.

## What the parser commit says about itself

The Postgres guard is careful about its own status. It calls itself defense-in-depth, not a security boundary, and names the authoritative control as the least-privilege database role. AWS says the same in both advisories. That is the correct position, and it is worth sitting with, because it means the read-only switch in a tool server was never the enforcement point. The grant is. A log of what the agent asked for proves what happened; only the role decides what can happen.

Which leaves a question the repository has now put to itself twice. The Redshift server switched to a parser in June. Postgres switched on 11 September. A parse tree cannot be fooled by whitespace, comments, case or Unicode escapes, because it is not reading text. A keyword list can be fooled by all four, and each one costs an advisory and a release to find out about. Four of these servers are still on the keyword list. Two of them have stopped, and the newer one's own comment explains why.
