# Hooks and permissions

Follow `.claude/workflows/sophon-workflow.md`. Do not assume a machine has particular global hooks, formatters or editors. The repository's `.claude/hooks/check-format.sh` is an explicitly callable syntax helper; its existence does not register an automatic hook.

Inspect active hook/permission sources only when a task changes them or observed behavior requires diagnosis. Preserve applicable ask/deny controls and do not bypass a permission rejection, enable dangerously-skip-permissions, or change global permission mode to complete a routine task.

Update the existing plan/check records for planned work; a todo view can summarize them but does not replace approval evidence. Generic hook advice adds no mandatory command chain, editor launch or unrelated language check.
