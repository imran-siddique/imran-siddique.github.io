---
title: The tool list was advertised, the resolver decided
date: 2026-08-24
standfirst: Spring AI released a fix on 21 August for a bug where a tool absent from the request could still be called. The vulnerable dispatch is one line. The public fix exists on one of the three affected release lines, and the fallback left almost nothing useful in the log.
tags: [agent-security, tool-calling, enforcement]
sources:
  - label: Spring advisory CVE-2026-59318, published 20 August 2026
    url: https://spring.io/security/cve-2026-59318/
  - label: Spring AI 2.0.1 release announcement, 21 August 2026
    url: https://spring.io/blog/2026/08/21/spring-ai-2-0-1-available-now/
  - label: Spring AI 2.0.1 upgrade notes, tool resolution fallback
    url: https://docs.spring.io/spring-ai/reference/upgrade-notes.html#_tool_resolution_fallback_disabled_by_default
  - label: DefaultToolCallingManager at v2.0.0, the vulnerable fallback
    url: https://github.com/spring-projects/spring-ai/blob/v2.0.0/spring-ai-model/src/main/java/org/springframework/ai/model/tool/DefaultToolCallingManager.java
  - label: DefaultToolCallingManager at v2.0.1, the disabled-by-default fallback
    url: https://github.com/spring-projects/spring-ai/blob/v2.0.1/spring-ai-model/src/main/java/org/springframework/ai/model/tool/DefaultToolCallingManager.java
  - label: StaticToolCallbackResolver at v2.0.1, registry lookup and debug log
    url: https://github.com/spring-projects/spring-ai/blob/v2.0.1/spring-ai-model/src/main/java/org/springframework/ai/tool/resolution/StaticToolCallbackResolver.java
  - label: Maven Central, public spring-ai-model versions
    url: https://repo1.maven.org/maven2/org/springframework/ai/spring-ai-model/
  - label: cMCP LIMITATIONS.md, gateway enforcement boundary
    url: https://github.com/agentrust-io/cmcp/blob/main/LIMITATIONS.md
---

Here is the vulnerable path in `DefaultToolCallingManager` at tag `v2.0.0`:

```java
ToolCallback toolCallback = toolCallbacks.stream()
    .filter(tool -> toolName.equals(tool.getToolDefinition().name()))
    .findFirst()
    .orElseGet(() -> this.toolCallbackResolver.resolve(toolName));
```

`toolCallbacks` is the list attached to this request. It is also the list advertised to the model.

If the model returns a name that is absent from that list, execution does not stop. The manager falls through to a resolver that has no knowledge of the request.

Spring's advisory describes the distinction precisely: the per-request tool list was advertised as a boundary but was not fully enforced during dispatch.

Sit with the word *advertised*. The boundary was something said to the model. The thing that actually decided was a lookup in a map.

## What the map holds

`StaticToolCallbackResolver` holds a map keyed by tool name. Its `resolve` operation is a lookup in that map. `DelegatingToolCallbackResolver` walks its configured resolvers and returns the first non-null result. Neither carries the request's advertised tool set.

For the built-in resolvers, the per-request list governed what the model could see. The resolver governed what the process could execute.

The evidence gap follows the enforcement gap. A successful fallback produced no fallback-specific log in the manager. The static resolver emits a debug message, but the message does not include the tool name.

Enforcement did not run. Separately, the evidence needed to reconstruct the bypass was not written either. An audit log cannot tell you which unadvertised tool was resolved if the resolution event never names it.

## The shape of the fix

At `v2.0.1`, the dispatch line became:

```java
.orElseGet(() -> this.resolutionFallbackEnabled
        ? this.toolCallbackResolver.resolve(toolName)
        : null);
```

The default is now `false`.

That is the right default for a library. It is still worth naming what kind of control it is: an in-process default that an application can reverse.

Spring documents two ways to restore the old behaviour. Direct users can set `.resolutionFallbackEnabled(true)` on the builder. Spring Boot users can set:

```properties
spring.ai.tools.resolution.fallback.enabled=true
```

Dynamic tool resolution is a legitimate requirement. But once fallback is restored, the request's advertised list is no longer the complete execution boundary. That choice needs its own policy and evidence, not merely a configuration value.

## Which line got the public fix

The advisory identifies three affected release lines:

- `1.0.0` through `1.0.9`
- `1.1.0` through `1.1.8`
- `2.0.0`

Its fix table contains four versions. `2.0.1` is marked OSS. `2.0.0.1`, `1.1.9`, and `1.0.10` are marked Enterprise Support Only.

That is a published commercial support model doing what it says it does. It is not a scandal. It does change the usual "upgrade to 2.0.1" summary.

For someone already on `2.0.0`, the public fix is a patch bump. For someone on either affected 1.x line, the publicly available route is a major-version migration. The advisory's table says that plainly.

I also dropped the CVSS number. The vector published by Spring did not reconcile with one score presented during checking, so this note uses Spring's **Medium** severity label and makes no numerical claim.

## Where I sit in it

cMCP enforces policy where tool calls cross its gateway. Its limitations already say that the gateway controls the tool boundary, not the model boundary, and that protection does not apply when a call bypasses the gateway.

A callback resolved from a local Java registry is an in-process method call. It never crosses an MCP boundary. My gateway would not see it, deny it, or place it in its audit chain.

That does not make the gateway control wrong. It identifies its enforcement domain.

A control plane that observes calls leaving a process governs one class of tool execution. CVE-2026-59318 lived in the other class. I do not know how many deployed applications re-enable the fallback or otherwise resolve tools inside the process.
