# Coding Style

Prefer existing repository conventions and scoped language rules. Apply `.claude/workflows/sophon-workflow.md` to execution and review; style guidance does not create a mandatory checklist, dependency or unrelated refactoring task.

## State and Ownership

Prefer immutable transformations where they fit the language and domain. Mutation within an established owner is appropriate when it preserves lifetime, threading and contracts; do not copy mutable state merely to satisfy generic immutability guidance. Keep one source of truth. These JavaScript examples illustrate alternatives, not a universal no-mutation rule:

```javascript
// In-place update: requires appropriate ownership
function updateUser(user, name) {
  user.name = name  // MUTATION!
  return user
}

// Immutable update: useful when shared-state semantics call for it
function updateUser(user, name) {
  return {
    ...user,
    name
  }
}
```

## File Organization

Prefer high cohesion and low coupling. Use file/function size and nesting as readability signals, not hard acceptance limits. Extract code only when the requested change needs a real boundary; do not split existing files or create utilities solely to meet a line-count target. Organize new code by the existing feature/domain pattern.

## Error Handling

ALWAYS handle errors comprehensively:

```typescript
try {
  const result = await riskyOperation()
  return result
} catch (error) {
  console.error('Operation failed:', error)
  throw new Error('Detailed user-friendly message')
}
```

## Input Validation

ALWAYS validate user input:

```typescript
import { z } from 'zod'

const schema = z.object({
  email: z.string().email(),
  age: z.number().int().min(0).max(150)
})

const validated = schema.parse(input)
```

## Code Quality Checklist

For affected code, consider these quality goals; they are not an additional completion gate:
- Code is readable and well-named
- Functions are focused and understandable
- Files are cohesive; size limits are advisory
- Nesting remains understandable
- Proper error handling
- No console.log statements
- No hardcoded values
- State changes respect explicit ownership, lifetime and threading contracts
