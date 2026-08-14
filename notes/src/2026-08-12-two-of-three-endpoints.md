---
title: Two of the three endpoints checked authorization
date: 2026-08-12
standfirst: The gym booking story is being told as an API with no authorization. The agent's own account says two of the three operations it touched returned 403, and one did not.
tags: [agent-security, api, authorization]
linkedin: https://www.linkedin.com/feed/update/urn:li:activity:7493162767328206849/
sources:
  - label: The Next Web, coverage carrying the agent's second message
    url: https://thenextweb.com/
  - label: The Register, coverage quoting ABC News (Australia), 10 August 2026
    url: https://www.theregister.com/
  - label: OWASP API Security Top 10, API1 Broken Object Level Authorization
    url: https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/
  - label: openclaw/openclaw star count read at api.github.com, 12 August 2026
    url: https://api.github.com/repos/openclaw/openclaw
---

An Australian man asked his personal assistant agent to book him a gym class. He was fourth on the waitlist. Minutes later he was third, because the agent had cancelled the booking of the person in first place.

The agent explained itself in plain text, and its wording matters:

> the API has zero authorisations checks on cancelling other people's reservations

Nothing was jailbroken. There was no prompt injection. The agent read the API and used it exactly as documented.

## The detail that changes the story

Most coverage stopped at "the API had no authorization". The agent's second message, which one outlet carried and the rest did not, says something more specific: `createReservation` and `joinWaitlist` both returned 403 Forbidden. Only `cancelReservation` was missing the ownership check.

So this was not a platform built without a security model. It was a platform with a security model and one handler where somebody forgot to apply it. Two of the three operations the agent touched behaved correctly.

That is a much more uncomfortable finding, because "we never did authorization" is a project you can schedule and "one of our handlers is missing a check" is a condition every codebase is in right now and cannot easily prove it is not.

I am scoping that carefully on purpose. Three operations were reported. That says nothing about how many endpoints the booking platform has, and I do not know the ratio. When I first wrote this up I said "two thirds of the API worked", which generalises three data points to a whole system, and I had to correct it after publishing. The honest statement is the narrow one.

## What kind of bug this is

Broken Object Level Authorization: the caller is authenticated, the caller is permitted to invoke the operation, and nobody checks that the caller owns the specific object being operated on. It is the first entry on the OWASP API Security Top 10, and it has been for years.

The gap was presumably always there. Human customers only ever clicked the buttons the web interface gave them, and the interface never offered to cancel a stranger's reservation. The agent is not a new class of attacker. It is the first client in that API's history that tried every request the API allowed.

The missing control is per-request object authorization: does this caller own this object, not is this caller logged in. It has to run in the endpoint's own handler, on the server, next to the data that answers the question.

## Why my own layer would not have caught it

AGT puts a deterministic policy engine between an agent and its tools, with no model anywhere in the safety path. On this incident it would have seen the agent issue a cancel call. It would not have known the reservation belonged to a stranger, because that fact lives in the gym's database and appears nowhere in the request.

A governance layer on the agent's side cannot make a check that only the server can make. This is the boundary, and I would rather state it than let a diagram imply otherwise.

There is a second thing worth separating, because I blurred it in the first version of this and it is worth not repeating. Enforcement runs at the service, before the operation executes, and it prevents. Evidence is written after the fact, it is tamper-evident, and it proves. A log would not have saved the person whose class was cancelled. It would only have made the conversation afterwards short.

OpenClaw was at 385,960 stars when I read the repository. Every latent authorization gap in your API now has a client that will find it, and it will find it while trying to be helpful.

## What did not survive checking

- One outlet placed the man in Melbourne. The Register says only "Australian" and the other coverage names no city, so the city is not here.
- Reports of how far ahead the agent could book range from "several weeks" to "months", so no number is here either.
- Several outlets called this Australia's first autonomous cyberattack. That is a characterisation and not a finding, and it argues the story on the wrong axis.
- The original ABC News report is the primary source. abc.net.au blocks the crawler I use, so I have not read it directly. Everything above comes from two outlets that quote it and agree with each other.
