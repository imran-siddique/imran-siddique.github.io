---
title: The alias check I wired up was bypassed in September 2025
date: 2026-09-15
standfirst: DDRop landed on 14 September and walks past the platform appraisal policy I shipped three weeks ago. Reading it sent me to a paper from last year that had already walked past the same check, by the same four people, for under $50.
tags: [attestation, sev-snp, evidence]
x: https://x.com/mosiddi/status/2099950158092140998
sources:
  - label: DDRop paper, read 15 September 2026
    url: https://ddropattack.eu/ddrop.pdf
  - label: ddropattack/ddrop, the authors' repository
    url: https://github.com/ddropattack/ddrop
  - label: Battering RAM, disclosed 30 September 2025
    url: https://batteringram.eu/
  - label: AMD security bulletin SB-3048, revision 1.0 of 14 September 2026
    url: https://www.amd.com/en/resources/product-security/bulletin/amd-sb-3048.html
  - label: AMD security bulletin SB-3024, the Battering RAM advisory
    url: https://www.amd.com/en/resources/product-security/bulletin/amd-sb-3024.html
  - label: Intel security announcement INTEL-2026-08-11-001-DDROP
    url: https://www.intel.com/content/www/us/en/security-center/announcement/intel-security-announcement-2026-08-11-001.html
  - label: agent-manifest LIMITATIONS.md, the platform appraisal section
    url: https://github.com/agentrust-io/agent-manifest/blob/main/LIMITATIONS.md
  - label: go-sev-guest PR 200, merged 14 September 2026
    url: https://github.com/google/go-sev-guest/pull/200
---

Two things happened on 14 September. Google merged my documentation fix to go-sev-guest, closing the issue I filed in August about which `PlatformInfo` fields are ceilings and which are floors. And DDRop was published.

DDRop is a DDR5 RDIMM interposer from KU Leuven, ETH Zurich, Durham and Google, going to CCS in November. It injects parity errors on the command and address lines so the register clock driver rejects the command, then disconnects the ALERT line so the CPU is never told to re-issue it. Writes are silently discarded. The paper's first contribution line puts the build at under $200. Table 1 puts the commercial equivalent, Membuster on DDR4, at about $170,000.

Intel TDX, Intel Scalable SGX and AMD SEV-SNP are all affected, because, in the authors' words, "to maintain memory performance, scalable cloud TEEs omit cryptographic freshness guarantees". The processor can tell that memory is encrypted. It cannot tell that it is current.

Three weeks ago I shipped `appraise_platform_info` into agent-manifest so a verifier could require `alias_check_complete`, the bit where AMD firmware reports that its boot-time DRAM alias check finished and found nothing. I wrote in LIMITATIONS.md that this "lets a verifier insist the silicon says it did its own check".

## The part I got wrong, and it is not DDRop

DDRop has overtaken the check. That framing also lets me off.

The check was already bypassed when I shipped it. Battering RAM, disclosed on 30 September 2025, is a $47.62 DDR4 interposer that sits in the memory path "behaving transparently during startup and passing all trust checks", then flips to malicious at runtime. Its own summary says it "can circumvent Intel's and AMD's boot-time alias checks" and that it "breaks SEV's attestation feature on fully patched systems". AMD advised on it as SB-3024. Four of its authors are DDRop authors.

So on 20 August I required a bit whose published bypass was ten months old, and I described it as the one platform assertion bearing on physical access. Across agent-manifest, trace-spec, cmcp and ca2a, and across all twelve notes on this site, the string `battering` appears zero times. I had read about BadRAM and cited SB-3015. I had not read the paper that followed it.

## What DDRop adds

DDRop is not the same attack. Aliasing by grounding address lines does not work on DDR5, where commands are multi-cycle and grounding two lines corrupts eight logical bits. Write suppression is the way in instead, at native bus speed with no downclocking.

Then section 6.3 does something the alias check was never in the conversation for. Using injected secure page table entries, an attacker gets plaintext write access to its own TD's control structure, overwrites its own MRTD at offset 0x240 with the victim workload's expected measurement, and clears a validity flag at 0x3F2 to force a recompute. The authors confirm "the quote returned by TDG.MR.REPORT now contains the maliciously injected launch measurement". Every check my offline TDX verifier performs still passes, because the report is genuine and it is the measurement that is a lie. The paper also notes that cryptographic integrity mode would stop its other two case studies and not this one, since the forged structure is written under the correct key, and that its own test BIOS could not confirm that.

## What the vendors actually said

The two responses are not the same and they are being reported as though they were.

AMD SB-3048 says the technique "falls outside the scope of the published threat model for SEV-SNP" and that AMD "does not plan to assign a CVE or release mitigations in response to this report". Intel's announcement also puts it outside the standard threat model, says nothing about CVEs either way, and then says Intel is evaluating hardening and detection, "including the development of Platform Owner Endorsements which enable remote parties to establish who is in physical possession of the hardware sensitive workloads are running on".

The out-of-scope position is not news from this week either. Both vendors took it a year ago, for Battering RAM.

## Where I land

The policy stays. It does what it says, and requiring the bit is still better than not requiring it, because it catches the lie BadRAM told, an SPD chip reporting a module larger than it is. What changes is the sentence around it, and LIMITATIONS.md now owes a line naming Battering RAM, which is the honest version of "does its own check".

The mitigation vectors I declined to appraise in August are the next question rather than a closed one. I said I would be guessing without hardware; I have SEV-SNP silicon and go-sev-guest v0.15.0 ships reference minimums to validate a mask against.

And I have been writing for months that no confidential computing silicon is custody grade against an adversary who owns the machine, treating custody as the thing outside the report by definition. A vendor has now said in a security advisory that it intends to put custody in the report. I do not know whether Platform Owner Endorsements will work, and a verifier cannot appraise a field that does not exist yet. But I stated that boundary as permanent, twice, and it is the second time in a month that something I filed under unattestable turned out to be somebody's roadmap.
