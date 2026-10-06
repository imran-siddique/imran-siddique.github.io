---
title: The documented install does not resolve
date: 2026-10-06
standfirst: OSSA's README tells you to install 0.6.0, which is not on npm. The version that installs cannot start. Eight files on the default branch give five answers to which version this is, and the project's own release check passes.
tags: [agent-security, provenance, release-engineering]
sources:
  - label: OSSA canonical repository on GitLab, default branch release/v0.6.x at 0bd0ab94
    url: https://gitlab.com/blueflyio/ossa/openstandardagents/-/tree/0bd0ab94
  - label: Release-prep commit 146e1eb2, 5 October 2026
    url: https://gitlab.com/blueflyio/ossa/openstandardagents/-/commit/146e1eb2
  - label: scripts/release-doctor.mjs at 0bd0ab94
    url: https://gitlab.com/blueflyio/ossa/openstandardagents/-/blob/0bd0ab94/scripts/release-doctor.mjs
  - label: release-state.json at 0bd0ab94
    url: https://gitlab.com/blueflyio/ossa/openstandardagents/-/blob/0bd0ab94/release-state.json
  - label: spec/v0.6/common/provenance.schema.json at 0bd0ab94
    url: https://gitlab.com/blueflyio/ossa/openstandardagents/-/blob/0bd0ab94/spec/v0.6/common/provenance.schema.json
  - label: The package on the npm registry, latest 0.5.6
    url: https://registry.npmjs.org/@bluefly/openstandardagents
---

On 5 October the OSSA repository prepared a 0.6.0 release and held it, with a 0.5.7 hotfix to ship first. The README on that branch says the current stable release is 0.6.0 and gives this install line:

```
npm install @bluefly/openstandardagents@0.6.0
```

npm answers ETARGET, no matching version found. The registry has published nothing for this package since 3 June.

OSSA, the Open Standard for Software Agents, is a vendor-neutral YAML contract for agent identity, capability boundaries and governance metadata. Development happens on GitLab, and the GitHub repository is a mirror last updated in May. The v0.6 tree on GitLab carries a provenance schema whose description says it links an object back to the run and the delegation that produced it, "so audit can reconstruct who acted, under whose authority, and in what run." That is the right thing to build, and it is why the rest of this matters.

## Which version is this

Eight files at one commit on the default branch give five different numbers.

- package.json and the README: 0.6.0.
- release-state.json: current 0.6.0, registry tag 0.5.6.
- .version.json: current 0.5.3, latest stable 0.5.2, spec version 0.5.3.
- .well-known/ossa.json, the discovery document: 0.5.2.
- llms.txt, the file an agent reads: `apiVersion: ossa/v0.5.2`.
- RELEASE-NOTES.md: headed v0.5.2.
- ai.json, the project descriptor: 0.5.1, with a trust tier of verified-signature.

The spec pointer is the one that bites. .version.json names 0.5.3 as the spec version. The README in the same tree says 0.5.3 was accidentally published during recovery, and not to use it.

## What the registry serves

npm resolves latest to 0.5.6, published 3 June. I installed it on Node 24: one package, no runtime dependencies, no deprecation warning. Then I ran the CLI it puts on the path. `ossa --version` and `ossa validate` both exit 1 with ERR_MODULE_NOT_FOUND: cannot find package `commander`.

The repository already knows. release-state.json deprecates 0.5.6 because the bin imports the unpublished `@bluefly/ossa-*` workspace packages and the root declares no dependencies. Both halves are true, and the first failure is neither. The shipped code imports three scoped workspace packages that are not on the registry, and four public packages (commander, yaml, did-resolver, web-did-resolver) that are on it and were never declared. commander is the first import in the entrypoint, so commander is what breaks.

The deprecation that would have warned me is not on the registry either. 0.5.3, 0.5.4 and 0.5.5 carry deprecation text there; 0.5.6 does not. The live text on 0.5.4 says to use 0.5.1 until a corrected patch ships, while the repository's copy of that entry says to use 0.6.0 or later. The registry's version is the one a terminal prints.

## The gate that passed

The project does have a release check. `release:doctor` runs scripts/release-doctor.mjs as the last step of `release:check`, and its comments say a stable-version drift "still fails closed." It compares two things: that the README's install line and its "Current stable release" line both name the version in package.json.

Both name 0.6.0. I ran the script against the README and package.json at 0bd0ab94, on the release branch. It printed `RELEASE_DOCTOR_PASS` and exited 0.

It never asks the registry whether 0.6.0 exists, and it never opens .version.json, the discovery document or llms.txt. ai.json lists a `validate:versions` check for "Version consistency across package.json, .version.json, spec/, CHANGELOG.md"; package.json has no script by that name.

So the path has two checks. The one that refuses, npm's ETARGET, refuses the version the README recommends. The one the project wrote passes. A deprecation marker would not have changed either, because a marker prints and the install proceeds.

## Where to report it

The `bugs` field points at the GitLab issues page, which returns 404 to an anonymous visitor, and the issues API returns an empty list. Merge requests return 403. CONTRIBUTING.md and SECURITY.md both send you to wiki pages that return 404. The GitHub mirror has issues turned off. SECURITY.md's supported versions table lists 0.3.x and 0.2.x and nothing later, so the version you can install is not in it. Whether the GitLab tracker is disabled or limited to members, I cannot tell from outside.

## What a team can check

Agent provenance work tends to start one step late. The effort goes on signing the run, naming the actor and pinning the delegation. Before any of that, something has to say which version of the contract an agent was validated against, and say it once.

Two checks would have caught all of this, and both fit in a release script. Resolve the documented install against the registry before tagging: `npm view @bluefly/openstandardagents@0.6.0 version` fails with E404 today. And read every file that states a version, the ones agents read included, and fail on any disagreement. A provenance record can only name the contract an agent was held to if the contract has one name.
