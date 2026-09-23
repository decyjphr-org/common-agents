---
name: js-to-typescript
description: >
  Converts JavaScript applications to TypeScript with full type safety. Use this skill whenever
  a user wants to migrate, rewrite, convert, or port a JavaScript (.js, .jsx) codebase or file
  to TypeScript (.ts, .tsx). Triggers on phrases like "convert to TypeScript", "rewrite in TypeScript",
  "migrate to TypeScript", "add types to my JS", "TypeScript conversion", or any request to add
  static typing to a JavaScript project. Always use this skill even for single-file conversions,
  partial migrations, or when the user just wants to "add TypeScript" to an existing project.

---

# JS → TypeScript Migration Skill

A structured approach to converting JavaScript applications to TypeScript with high quality, idiomatic types.

---

## Phase 1: Assess the Project

Before writing any code, understand the scope:

1. **Scan the project structure**:

   ```bash
   find . -name "*.js" -o -name "*.jsx" | head -50
   ls package.json tsconfig.json 2>/dev/null
   ```

2. **Identify key concerns**:

   - Framework in use (Probot,  octokit, React, Node/Express, Next.js, Vue, plain JS, etc.)
   - Existing type definitions or JSDoc comments
   - External libraries that need `@types/` packages
   - Build tooling (webpack, vite, esbuild, tsc, etc.)
   - Test files (Jest, Vitest, Mocha) — convert these too

3. **Check if tsconfig exists** — if not, create one (see Phase 2)

---

## Phase 2: Setup TypeScript Config

If no `tsconfig.json` exists, create one appropriate to the project type.

### For Node.js / backend:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### For React / frontend:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["DOM", "DOM.Iterable", "ES2020"],
    "jsx": "react-jsx",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "outDir": "./dist",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "allowImportingTsExtensions": true,
    "noEmit": true
  },
  "include": ["src"],
  "exclude": ["node_modules"]
}
```

### Update package.json dependencies:

```bash
npm install --save-dev typescript @types/node
# For React:
npm install --save-dev @types/react @types/react-dom
# For Express:
npm install --save-dev @types/express
# Run: npx tsc --noEmit to check for errors
```

---

## Phase 3: File-by-File Conversion Rules

### Rename files:

- `.js` → `.ts`
- `.jsx` → `.tsx`

### Core TypeScript patterns to apply:

#### 1. Function signatures — always type parameters and return values

```typescript
// Before (JS)
function fetchUser(id) {
  return db.find(id);
}

// After (TS)
async function fetchUser(id: string): Promise<User | null> {
  return db.find(id);
}
```

#### 2. Variables — infer where possible, annotate where needed

```typescript
// TS can infer: const name = "Alice"  →  string
// Annotate when initializing to null/undefined:
let currentUser: User | null = null;
```

#### 3. Objects — define interfaces or types

```typescript
// Before
const user = { id: '1', name: 'Alice', age: 30 };

// After — define reusable interface
interface User {
  id: string;
  name: string;
  age: number;
  email?: string; // optional field
}
const user: User = { id: '1', name: 'Alice', age: 30 };
```

#### 4. Arrays

```typescript
const ids: string[] = [];
const users: User[] = [];
const matrix: number[][] = [[1, 2], [3, 4]];
```

#### 5. React components

```typescript
// Functional component with props
interface ButtonProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary';
}

const Button: React.FC<ButtonProps> = ({ label, onClick, disabled = false, variant = 'primary' }) => {
  return <button onClick={onClick} disabled={disabled}>{label}</button>;
};
```

#### 6. Event handlers

```typescript
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  setValue(e.target.value);
};

const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
};
```

#### 7. Async/Promises

```typescript
async function getData(): Promise<ApiResponse> {
  const res = await fetch('/api/data');
  if (!res.ok) throw new Error(`HTTP error: ${res.status}`);
  return res.json() as Promise<ApiResponse>;
}
```

#### 8. Error handling

```typescript
try {
  await riskyOperation();
} catch (error) {
  if (error instanceof Error) {
    console.error(error.message);
  }
}
```

#### 9. Union types for flexibility

```typescript
type Status = 'idle' | 'loading' | 'success' | 'error';
type ID = string | number;
```

#### 10. Generics for reusable code

```typescript
function first<T>(arr: T[]): T | undefined {
  return arr[0];
}

interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
}
```

#### 11. Type assertions (use sparingly)

```typescript
// Only when you know more than TypeScript does
const canvas = document.getElementById('canvas') as HTMLCanvasElement;
```

#### 12. Enums for named constants

```typescript
enum Direction {
  Up = 'UP',
  Down = 'DOWN',
  Left = 'LEFT',
  Right = 'RIGHT',
}
```

---

## Phase 4: Handling Common Patterns

### Dynamic/unknown objects from APIs

```typescript
// Use `unknown` and narrow it:
async function parseResponse(data: unknown): Promise<User> {
  if (typeof data !== 'object' || data === null) {
    throw new Error('Invalid response');
  }
  // Use a validation library (zod) or type guard
  return data as User;
}

// Or use type guards:
function isUser(obj: unknown): obj is User {
  return typeof obj === 'object' && obj !== null && 'id' in obj && 'name' in obj;
}
```

### `this` context in classes

```typescript
class EventEmitter {
  private listeners: Map<string, ((data: unknown) => void)[]> = new Map();

  on(event: string, listener: (data: unknown) => void): this {
    // ...
    return this;
  }
}
```

### Extending built-in types

```typescript
interface Window {
  myCustomGlobal: string;
}
```

### Default exports vs named exports

```typescript
// Named (preferred for most cases):
export interface User { ... }
export function createUser(): User { ... }

// Default (for components, main class):
export default function App() { ... }
```

---

## Phase 5: Common `@types` Packages

Install as needed based on dependencies found in `package.json`:

| Library | Types package                   |
| ------- | ------------------------------- |
| express | `@types/express`                |
| lodash  | `@types/lodash`                 |
| node    | `@types/node`                   |
| react   | `@types/react @types/react-dom` |
| jest    | `@types/jest`                   |
| mocha   | `@types/mocha @types/chai`      |
| cors    | `@types/cors`                   |
| uuid    | `@types/uuid`                   |
| bcrypt  | `@types/bcrypt`                 |
| multer  | `@types/multer`                 |

---

## Phase 6: Strict Mode Pitfalls & Fixes

With `strict: true`, these patterns commonly fail:

| Error                                                   | Fix                                          |
| ------------------------------------------------------- | -------------------------------------------- |
| `Object is possibly 'null'`                             | Add null check: `if (el) { el.style... }`    |
| `Parameter 'x' implicitly has 'any' type`               | Add explicit type annotation                 |
| `Property 'x' does not exist on type '{}'`              | Define proper interface                      |
| `Type 'string \| undefined' not assignable to 'string'` | Use `??` or non-null assertion `!` with care |
| `Unsafe member access on 'any'`                         | Narrow type with type guard                  |

---

## Phase 7: Validation Checklist

After conversion, verify:

- [ ] `npx tsc --noEmit` runs with 0 errors
- [ ] No `any` types except where explicitly justified (use `// eslint-disable-next-line @typescript-eslint/no-explicit-any` if truly needed)
- [ ] All exported functions have explicit return types
- [ ] All interfaces/types are exported if used across files
- [ ] All third-party libraries have `@types/` packages or built-in types
- [ ] Tests still pass
- [ ] No implicit `any` from missing `@types` packages

---

## Tips for Quality Output

- **Prefer `interface` over `type` for object shapes** (easier to extend)
- **Use `type` for unions, intersections, mapped types**
- **Avoid `any`** — use `unknown` and narrow it instead
- **Prefer `readonly` arrays** where mutation isn't needed: `readonly string[]`
- **Use utility types** like `Partial<T>`, `Required<T>`, `Pick<T, K>`, `Omit<T, K>`, `Record<K, V>`, `ReturnType<T>`, `Parameters<T>`
- **Co-locate types with their usage** unless shared across many files (then put in `types/` or `@types/`)
- **Leverage inference** — don't annotate what TypeScript can figure out