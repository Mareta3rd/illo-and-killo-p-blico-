# Codex Execution Bridge

## Purpose

The execution bridge is the first runtime layer between the provider-neutral
`CodexTask` contract and a concrete Codex environment.

It deliberately does not know how Codex is invoked. That responsibility belongs
to a transport adapter.

```text
Ricard Digital / Core
        |
        v
   CodexTask
        |
        v
CodexExecutionBridge
        |
        v
  CodexTransport
        |
        v
   Codex environment
        |
        v
CodexTaskResult
        |
        v
scope + digest validation
```

## Boundary

The bridge performs four checks:

1. the input is a valid `CodexTask`;
2. explicit human approval is present before execution;
3. the transport returns a `CodexTaskResult`;
4. the result matches the task identity/digest and stays inside the task scope.

An unapproved task returns `blocked` without calling the transport.
A malformed or out-of-scope transport result is rejected rather than silently
converted into a successful result.

## Provider neutrality

`CodexTransport` is a minimal protocol. A future real Codex adapter can implement
it without changing Core or the task contract.

The first implementation intentionally uses no live Codex API assumptions. The
real transport belongs to a later integration block after the current bridge
contract is verified.

## Canon and authority

The bridge does not grant Codex any authority over canon, Core decisions or
creative policy. It only controls execution of an already-scoped task.

A `completed` result is still not an integration decision; normal tests, diff
inspection, review and work-block closure remain required.