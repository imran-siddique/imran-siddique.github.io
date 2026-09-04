---
title: The finding was correct and eight weeks late
date: 2026-09-02
standfirst: A gap in the SEAT post-handshake attestation draft turned out to have been argued on the working group list in July, and specified in a closed issue a year before that. What I filed instead came from reading the RFCs the draft already cites.
tags: [attestation, tls, spec-review]
x: https://x.com/mosiddi/status/2095958403831226472
sources:
  - label: draft-fossati-seat-expat, source on GitHub
    url: https://github.com/tls-attestation/exported-attestation/blob/main/draft-fossati-seat-expat.md
  - label: SEAT list, The Passport Model-sized elephant in the room, 10 July 2026
    url: https://mailarchive.ietf.org/arch/msg/seat/Xwf2c1jfUWeGgHjWGFliKqtqANM/
  - label: exported-attestation issue 21, comment of 4 August 2025
    url: https://github.com/tls-attestation/exported-attestation/issues/21
  - label: exported-attestation issue 58, why the public key is hashed into the binder
    url: https://github.com/tls-attestation/exported-attestation/issues/58
  - label: RFC 8446 section 7.5, Exporters
    url: https://www.rfc-editor.org/rfc/rfc8446.html#section-7.5
  - label: RFC 5705 sections 4 and 6, exporter label format and registry
    url: https://www.rfc-editor.org/rfc/rfc5705.html#section-4
  - label: IANA TLS Parameters, Exporter Labels registry
    url: https://www.iana.org/assignments/tls-parameters/tls-parameters.xhtml
  - label: exported-attestation issue 63, filed 2 September 2026
    url: https://github.com/tls-attestation/exported-attestation/issues/63
---

The gap I had found was real, and somebody had already said so. Nathanael Ritz put it to the SEAT
mailing list on 10 July, quoting the same sentence I had marked, making the argument in more detail
than I had, and grounding it on the working group charter rather than on the document's abstract.
Two people replied substantively the same day. My contribution would have been to say it again,
later, and worse, to the people who had already had the conversation.

That is the case for checking prior art before you verify anything, rather than after. Verification
is the expensive step and it answers the second question.

## The document

`draft-fossati-seat-expat` moves remote attestation out of the TLS handshake and into RFC 9261
exported authenticators, after intra-handshake attestation was shown to permit relay attacks. Its
own appendix gives the motive: the older design "does not bind the Evidence to the application
traffic secrets, resulting in relay attacks".

## What I nearly filed

The abstract promises the approach "supports both the passport and background check models" while
attestation "remains bound to the underlying communication channel". The Terminology section defines
"attestation credentials" as covering both Evidence and attestation results. Every binding
requirement in the document then names Evidence and only Evidence. A word-boundary grep for `result`
across the binding section returns zero. The passport branch's sole requirement is that the
Attestation Result is correctly signed and meets policy.

All true, and all previously observed. Ritz quoted that same passport bullet in July. Worse for my
version, a comment on issue 21, closed, filed under the title "Misleading Finished Message" and
ostensibly about a diagram, had already asked "What binds the attestation results to the handshake?"
in August 2025 and specified the fix: carry `certificate_request_context` to the Verifier as `rdata`
and have it reflected into the Attestation Result. Running `git log -S rdata` over the draft source
returns nothing. The mechanism was designed, recorded in a thread about a figure, and lost.

## What I filed instead

The draft specifies the TLS exporter label twice, and spells it differently each time. Section 4
says the verifier recomputes the exporter value "using the label Attestation Binding". Section 5.1
says the invocation uses "the label Attestation", and prints
`TLS-Exporter("Attestation", certificate_request_context, 32)`. The label is an input to
`Derive-Secret`, so two implementations that each follow one section derive different values and
every binding check between them fails. Both spellings are in the published -03.

The part that makes it more than an editorial nit came from the draft's own citations. RFC 8446
section 7.5 says requirements for exporter label format are defined in section 4 of RFC 5705. That
section says all label values "MUST be registered via Specification Required". Section 6 adds that
IANA "MUST also verify that one label is not a prefix of any other label". `Attestation` is a prefix
of `Attestation Binding`, so the two can never both be registered, whichever section the working
group prefers. Neither is registered today; the draft's IANA section registers only the extension
type, and the string `attestation` does not appear anywhere in the TLS parameters registry.

## What did not survive checking

The novelty of the lead, entirely, for the reasons above. The claim was verified and the finding was
spent.

Also the assumption underneath it. I had been treating the requirement that Evidence carry a hash of
the authenticator identity key as settled ground, the fixed half against which the passport half
looked unfinished. Issue 58 is an open challenge to exactly that requirement, asking why the public
key needs hashing into the binder at all when the exported key material is already bound to the
session, with a co-author answering that he cannot say more until the formal analysis is done.
Building on it as a solved baseline would have walked into a live dispute.

Two counts were wrong in the version I started from: the file is 35,398 bytes rather than 34,900,
and "Attestation Result" occurs 22 times rather than 20. Neither touches the load-bearing claim,
which is that none of those occurrences falls in the binding or freshness sections.

If you are reading an unfamiliar draft, the two greps that pay are these. Take every value it
defines and check it against the registry that owns that namespace. Then take every specification it
cites normatively and read what that document actually requires. Both are cheap, both produce
findings its authors have already agreed to be bound by, and neither asks you to know anything they
do not.
