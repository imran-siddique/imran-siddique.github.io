---
title: The platform bit that means the opposite of what the doc says
date: 2026-08-20
standfirst: Google Cloud tells you to update go-sev-guest so your parser stops breaking on v4 attestation reports. I wanted to know what you can actually check once it parses, and the answer sent me to look at my own verifier.
tags: [attestation, sev-snp, evidence]
linkedin: https://www.linkedin.com/feed/update/urn:li:activity:7496285113891057664/
x: https://x.com/mosiddi/status/2090951455545163867
sources:
  - label: google/go-sev-guest validate.go at c930ed67, read 20 August 2026
    url: https://github.com/google/go-sev-guest/blob/c930ed67bebfe7245c0309888ec185bd9ad35899/validate/validate.go
  - label: google/go-sev-guest abi.go at c930ed67, the SnpPlatformInfo struct
    url: https://github.com/google/go-sev-guest/blob/c930ed67bebfe7245c0309888ec185bd9ad35899/abi/abi.go
  - label: Issue 195, the doc bug I filed against go-sev-guest
    url: https://github.com/google/go-sev-guest/issues/195
  - label: Issue 187, milesdai on TSME polarity, open since April 2026
    url: https://github.com/google/go-sev-guest/issues/187
  - label: Google Cloud Confidential VM release notes, entry of 27 October 2025
    url: https://docs.cloud.google.com/confidential-computing/confidential-vm/docs/release-notes
  - label: BadRAM
    url: https://badram.eu/
  - label: AMD security bulletin SB-3015
    url: https://www.amd.com/en/resources/product-security/bulletin/amd-sb-3015.html
---

I set out to answer a small question this morning, and it cost me more than I expected.

Google Cloud's Confidential VM release notes, in an entry dated 27 October 2025, say that after a firmware update SEV-SNP instances generate v4 attestation reports and that parsers written for v3 might break. The fix offered is to update go-sev-guest to v0.14.0 or above. That advice is correct. I wanted to know what you can check once the thing parses.

## The version the advice names cannot check what it reads

The v4 report added two mitigation vectors, `LAUNCH_MIT_VECTOR` and `CURRENT_MIT_VECTOR`, at offsets 0x1F8 and 0x200. They carry which platform-level mitigations were in force at launch and which are in force now.

At v0.14.0, tagged 9 October 2025, the `abi` package reads both. The `validate` package does not contain the string "mitigation" anywhere. There is no option to require anything of those vectors and no function that looks at them. Same at v0.14.1.

The policy hooks arrive in v0.15.0, tagged 9 June 2026 and still the latest release: `MinimumLaunchMitigationVector`, `MinimumCurrentMitigationVector`, and a check wired into the main validation path.

That is not a scandal. Libraries grow, and the option did not exist anywhere in the interval, so nobody was exposed by choosing wrongly. But "update to v0.14.0 or above" answers the question people asked, which was why their parser crashed, and not the question worth asking, which is what the new report says and whether anyone is reading it.

## Four of seven fields mean the opposite of the documentation

The second half is a documentation problem rather than a code one.

The library's platform-info policy field is documented as a ceiling. The doc comment says `PlatformInfo` is the maximum of acceptable data. The README says each true field is permission for the corresponding report bit to be set. Read that and you build a policy by deciding what you will tolerate.

Then read the function. The struct has seven fields. Three behave that way: SMT, TSME and SEV-TIO all fail with "unauthorized" when the report carries a bit your policy did not grant.

The other four are reversed. ECC, RAPL disabled, ciphertext hiding and alias-check-complete all fail when the report is *missing* something your policy asked for. For those, setting the bit true is not permission. It is a demand.

The one I care about is alias-check-complete. The comment above it in the source names what it is for and links to BadRAM and AMD's bulletin SB-3015. The firmware's alias check is the thing that prevents. The bit in the report only proves the firmware ran it. A verifier can require that proof, and under the documented model an operator has no reason to, because they are not trying to authorise anything. They leave it false and the requirement never runs.

## What did not survive checking

The morning brief that pointed me here claimed nobody had made this argument before. Wrong. Issue 187 has been open since 16 April, unanswered, reporting the same confusion from the other end: that TSME can only be required to be off. I read that as evidence for the doc being the cause, and cited it.

It also had three of the four error strings wrong, and counted thirteen references where there are fifteen. I could not treat any of it as read.

I could not date the release note from search results either. It turned out to be ten months old, which is worth knowing before deciding anything is news.

## What this cost me

I went to check my own verifier before writing a word of this, and I did not enjoy the result.

`_snp_verify.py` in agent-manifest does not parse `PLATFORM_INFO` at all. The field sits at offset 0x40. My offset table goes from the signature algorithm at 0x34 straight to report data at 0x50. It is not in the table, not in the parsed struct, and across every first-party file in agent-manifest, cmcp, ca2a and trace-spec the terms `platform_info`, `alias_check`, `mit_vector` and `badram` appear zero times each.

So this is not a case of my documents failing to mention a check that the code performs. The bytes are never read. What my verifiers do establish is real and fail-closed: report signature, the VCEK to ASK to ARK chain with the root pinned by the operator, measurement binding. That is authenticity and identity. None of those four asks the report what kind of machine it came from.

I have written the honest limit the same way for months, that no confidential computing silicon is custody grade against an adversary who owns the machine, with BadRAM as the reason. I treated it as a boundary to state and live with. Part of it is a boundary you can assert on, and AMD put the bit in the report to let you.

## What changed today

I filed issue 195 against go-sev-guest, proposing the doc comment and the README bullet be split into the ceiling set and the floor set, with the fields named in each.

Parsing `PLATFORM_INFO` and exposing an appraisal policy over it goes into agent-manifest next, and the limitations files across all four repos get a line naming what is not checked. Not everything unenforced is unenforceable. Sometimes the check is sitting in the struct and nobody wired it up.
