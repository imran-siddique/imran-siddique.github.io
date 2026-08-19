---
title: The attestation everyone cites cannot be looked up any more
date: 2026-08-19
standfirst: Thirty poisoned npm packages are gone along with their attestations, and the Sigstore copy that survives can only be fetched with a digest that no longer exists in any public place I could find.
tags: [supply-chain, evidence, provenance]
sources:
  - label: Aikido, "Keyv and friends compromised in npm supply chain attack", 4 August 2026
    url: https://www.aikido.dev/blog/keyv-and-friends-compromised-in-npm-supply-chain-attack
  - label: Snyk, "Inside the keyv npm compromise", read 19 August 2026
    url: https://snyk.io/blog/inside-keyv-npm-compromise-preinstall-malware-trusted-provenance-ide-hooks/
  - label: VentureBeat, "The Shai-Hulud npm worm didn't fake its security check, it earned a legitimate one"
    url: https://venturebeat.com/security/the-shai-hulud-npm-worm-didnt-fake-its-security-check-it-earned-a-legitimate-one
  - label: nulltap, "Keyv's signed npm releases carried a credential-stealing worm"
    url: https://nulltap.sh/p/keyv-shai-hulud-provenance/
  - label: npm registry packuments and attestation endpoints, read 19 August 2026
    url: https://registry.npmjs.org/keyv
  - label: Sigstore Rekor transparency log, search index API
    url: https://rekor.sigstore.dev/api/v1/log/entries?logIndex=2336496546
  - label: GitHub docs, retention period for Actions artifacts and logs
    url: https://docs.github.com/en/organizations/managing-organization-settings/configuring-the-retention-period-for-github-actions-artifacts-and-logs-in-your-organization
  - label: TRACE specification, LIMITATIONS.md
    url: https://github.com/agentrust-io/trace-spec/blob/main/LIMITATIONS.md
---

Every account of the keyv compromise turns on one sentence. Aikido's is representative: "the poisoned versions were published to npm with valid provenance signed by GitHub Actions." That is the detail that made this story worth writing about rather than another package takeover.

Fifteen days later I went to check it, and at npm you cannot.

## What is left

I fetched thirty packages this morning: the twenty that one release run published, and ten more across the maintainer's other projects. Every one behaves the same way. The poisoned version is absent from its packument's versions map, its tarball returns 404, and its attestation endpoint returns 404. A control fetch of a clean version returns 200 on all three.

One thing does survive. npm keeps the publish timestamp in the packument's time map for a version that exists nowhere else in the registry. Thirty orphan timestamps, running from 09:30:01.291Z to 10:28:01.451Z on 4 August, and nothing else.

Worth noting in passing, since it bears on every count you have read: the public indicator lists name eleven packages. The release run's own log ends with the line "Published 20 package(s)", from that one repository, before the campaign spread anywhere else. Thirty is a count of what I fetched, not a total.

## The copy that is still there

Deleting from npm does not delete the attestation. npm's provenance is written to Rekor, Sigstore's public append-only transparency log, and append-only means npm cannot take an entry back out.

The retrieval path works, and I checked that it works before concluding anything about the missing ones. keyv 6.0.0-rc.1, published the evening before the compromise and still live, has a tarball digest in its packument. Handing that sha512 to Rekor's search index returns two entries, which are the two Sigstore bundles npm attached to that release. Fetching one by its log index returns the record.

Now do the same for keyv 6.0.0. The digest lives in the packument's entry for that version, and the packument's entry for that version is exactly what unpublishing removes. The tarball is gone, so I cannot recompute it. npm's attestation endpoint, which would hand it over, is one of the ones returning 404. A public mirror I checked never carried the version at all. Rekor's index also accepts a certificate subject, so I tried the workflow identity instead, and it returned nothing for the poisoned build and nothing for the live control either, which tells me the method does not work rather than that the entry is missing.

So the entry is almost certainly sitting in the log, and I have no way to ask for it.

## Why I think this matters

Unpublishing was the right call and it did the job it was for. Enforcement runs at the registry, in front of the fetch, and it is what actually stops anyone installing keyv 6.0.0 today. Nothing here argues against it. The point sits next to it, not against it.

Evidence is a different job. It prevents nothing. Its whole value is that somebody who trusts neither the attacker nor the registry can come back later and check a claim. An append-only log answers the question "can this record be removed", which is the question everybody designs for. It does not answer "can this record be found", and that turns out to be the one that bites, because the address was carried by the artifact and the artifact is what you delete. The record outlived its index.

The one other place the build is documented is the workflow run at GitHub. Per GitHub's documented default those logs are deleted 90 days after the run, which for this incident falls in early November, and I could not read the repository's actual setting.

I have not answered this in my own work either. TRACE's limitations document says "Signature validity is permanent; trust is not. Nothing inside a record can retract the key that signed it", and the answer we specified is a revocation store the verifier consults at verification time. That handles a key being withdrawn. It says nothing about a record that stays perfectly valid and becomes unreachable because the thing it describes was deleted, and a content-addressed trust record has the same shape of problem as npm's.

## What did not survive checking

- **Whether the poisoned attestations are in Rekor.** I believe they are and I did not confirm it. Both routes failed for the reasons above, and the subject-index route failed its own control, so treat this as unproven rather than as a negative result.
- **The size of the campaign.** Aikido's page currently reads 444 packages across 1,381 versions; VentureBeat cites Aikido at 868; JFrog traced more than 400 packages and 1,700 versions. I did not resolve them, so no total appears above and none of the argument rests on one.
- **Whether the eleven named packages are the malicious set.** I can show that thirty were published in the window from the same runs and later removed. I cannot show what was in any of them, because the tarballs are gone. That is the same wall as everything else here.
- **The 90-day expiry.** That is GitHub's documented default. The repository's configured retention is not readable without access I do not have.
