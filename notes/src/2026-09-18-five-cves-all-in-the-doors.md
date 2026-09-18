---
title: Five Docker Sandboxes CVEs this year, all in the doors
date: 2026-09-18
standfirst: Docker published two more CVEs against its agent sandbox on 15 September. Read alongside the three it published in June and August, all five sit in the two controls its README sells, and three of them fail the same way.
tags: [agent-security, sandboxing, enforcement]
sources:
  - label: CVE-2026-77179, CVE Program record (virtio-fs, macOS, CVSS 4.0 9.4)
    url: https://github.com/CVEProject/cvelistV5/blob/main/cves/2026/77xxx/CVE-2026-77179.json
  - label: CVE-2026-79994, CVE Program record (Unix socket relay, CVSS 4.0 8.7)
    url: https://github.com/CVEProject/cvelistV5/blob/main/cves/2026/79xxx/CVE-2026-79994.json
  - label: CVE-2026-12039, NVD (DNS not covered by the egress allowlist)
    url: https://nvd.nist.gov/vuln/detail/CVE-2026-12039
  - label: CVE-2026-12539, NVD (ICMP authorizer not re-applied after daemon restart)
    url: https://nvd.nist.gov/vuln/detail/CVE-2026-12539
  - label: CVE-2026-18171, NVD (read-only mount writable at the virtio-fs export)
    url: https://nvd.nist.gov/vuln/detail/CVE-2026-18171
  - label: Docker Sandboxes v0.42.0 release notes, 7 September 2026
    url: https://github.com/docker/sbx-releases/releases/tag/v0.42.0
  - label: docker/sbx-releases README, read 18 September 2026
    url: https://github.com/docker/sbx-releases/blob/main/README.md
  - label: trace-spec LIMITATIONS.md, "Pure offline verification cannot prove non-revocation"
    url: https://github.com/agentrust-io/trace-spec/blob/main/LIMITATIONS.md
---

Five CVEs have been published against Docker Sandboxes this year, all by Docker as its own CNA. Two landed on 15 September, CVE-2026-77179 at CVSS 4.0 9.4 and CVE-2026-79994 at 8.7. Three came earlier: CVE-2026-12039 and CVE-2026-12539 in June, CVE-2026-18171 in August.

Docker Sandboxes runs each coding agent in its own microVM, which is the right design, and none of the five is in the hypervisor. Every one is in a component that exists to let something through it: the embedded DNS server, the ICMP egress authorizer, the virtio-fs host server (twice), and the guest to host Unix socket relay. Isolation in an agent sandbox is the wall minus every door you cut into it, and the doors are where this product has been breaking.

## The README names the doors

The README lists four things under "What you get". Two of them are "File access controls between host and sandbox" and "Network access control". Sort the five records by those two lines and nothing is left over. DNS and ICMP are network access. The two virtio-fs bugs and the socket relay are file access, the relay because it reaches host sockets by filesystem path.

The first item on the same list is "YOLO mode by default: agents work without asking permission." That is a reasonable default for a product whose pitch is that the agent can run unattended, and it means those two controls are standing in for the human who would otherwise approve each action. That is my reading of the document, not something Docker says.

## Three of the five made a decision once

This is the part worth taking to any sandbox, not only this one.

- CVE-2026-12539: ICMP egress is blocked "with an authorizer applied only at network-creation time", and not re-applied to networks rebuilt from disk after the Docker daemon restarts.
- CVE-2026-79994: the socket relay "validates that a socket path is inside an authorized workspace, but later reconnects using the pathname." A guest swaps an intermediate directory for a symlink in between.
- CVE-2026-77179: the virtio-fs server "improperly follows symlinks when reopening an unlinked file from a stored path."

None of these is a missing control. The relay's check ran and was correct when it ran. The ICMP authorizer ran and was correct when it ran. Each failed because its answer was treated as durable past the moment something could change underneath it: a path that can be relinked, a network that can be rebuilt. **An enforcement decision has a lifetime**, and in all three the lifetime was shorter than the code assumed.

I have the same shape written down about my own work. The trace-spec LIMITATIONS file says "Signature validity is permanent; trust is not", and requires a verifier to consult revocation status at verification time, with `verify_record()` failing closed when the revocation store cannot answer. Different substrate, same rule. The two honest fixes are the same in both places: bind the decision to the object you act on (an open file descriptor, not a name), or re-make it at the moment of use and fail closed when you cannot.

## What to ask on Monday

For each door a sandbox advertises, ask one question: when is this decision re-made? At creation only, at every connection, at every open, after a restart? If the vendor cannot answer, treat the control as holding until the first event that can invalidate it, and find out what those events are.

Two narrower things a team running this product can check today.

Platform scope. CVE-2026-77179 carries a platforms field set to MacOS and opens "On macOS". CVE-2026-79994 has no platforms field, and neither macOS nor Darwin appears anywhere in it. The README installs on macOS, Windows, Ubuntu and Rocky Linux 8. The record does not say the socket bug reaches Linux or Windows; it also does not say it is Mac only. If you run it off a Mac, read that record as applying to you.

Version. v0.42.0, released 7 September, fixes both new CVEs; the current stable is v0.43.0. The same 0.42.0 notes also say "Fixed a vulnerability where a sandboxed process could get the daemon to open a host D-Bus transport and execute an arbitrary command on the host." An NVD keyword search for Docker Sandboxes returns five records and none of them mentions D-Bus. That may simply not be assigned yet. It is a question for Docker, not a finding.

## What did not survive checking

"Neither is a VM escape." Both 15 September bugs let a malicious guest act on the host, and 77179 reaches arbitrary host files "potentially achieving host code execution". They are guest to host escapes. What holds is narrower: neither is in the hypervisor.

"Both helpers checked." Only the socket relay record describes a check. The virtio-fs record describes acting on a stored path, which is the same lifetime failure without a stated validation step.

"The 9.4 record points at no code, unlike the 8.7." True, and the wrong frame. None of the three earlier records points at code either. 79994 is the exception, citing a pull request in docker/sailor and one in docker/sandboxes, and neither repository resolves for an outside account, so the code is not public in any of the five.
