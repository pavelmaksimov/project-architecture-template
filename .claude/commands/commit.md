Generate a commit message from git diff following conventional commits specification.

Analyze the git diff and generate a commit message following these STRICT rules:

## Message Length Rules:
- Subject line: MAX 35 characters (50-72 preferred)
- If breaking change: MAX 100 characters allowed
- Use simple, clear English words

## Commit Types (from conventionalcommits.org):
The commit contains the following structural elements, to communicate intent to the consumers of your library:

fix: a commit of the type fix patches a bug in your codebase (this correlates with PATCH in Semantic Versioning).
feat: a commit of the type feat introduces a new feature to the codebase (this correlates with MINOR in Semantic Versioning).
BREAKING CHANGE: a commit that has a footer BREAKING CHANGE:, or appends a ! after the type/scope, introduces a breaking API change (correlating with MAJOR in Semantic Versioning). A BREAKING CHANGE can be part of commits of any type.
types other than fix: and feat: are allowed, for example @commitlint/config-conventional (based on the Angular convention) recommends build:, chore:, ci:, docs:, style:, refactor:, perf:, test:, and others.
footers other than BREAKING CHANGE: <description> may be provided and follow a convention similar to git trailer format.
Additional types are not mandated by the Conventional Commits specification, and have no implicit effect in Semantic Versioning (unless they include a BREAKING CHANGE).
A scope may be provided to a commit’s type, to provide additional contextual information and is contained within parenthesis, e.g., feat(parser): add ability to parse arrays.

## Message Format:
```
type(scope): subject

body (optional)

BREAKING CHANGE: description (if applicable)
footer: value (if applicable)
```

## Examples:
- `fix: prevent crash on login`
- `feat: add dark mode support`
- `feat(api)!: change authentication method`
- `chore!: remove deprecated code`
- `docs: update README installation section`
- `refactor(database): simplify query builder`

## Analysis Rules:
1. Determine the primary type based on changes
2. Check if any changes break backward compatibility
3. Choose appropriate scope (api, ui, db, auth, etc.)
4. Write clear, concise subject (action verb + what changed)
5. Keep subject under 35 chars (100 if breaking)
6. Use simple language for broad understanding

## Examples with BREAKING CHANGE:
```
feat!: send email when product ships
BREAKING CHANGE: email service no longer free

feat(api)!: change authentication method
BREAKING CHANGE: requires new token format

chore!: drop support for Node 6
BREAKING CHANGE: uses ES2015 features
```

No need to execute the commit command!
Return ONLY the commit message ready to use with `git commit -m "..."`,
3 options, short (up to 35 length) medium (50 to 90 length) and long (100 to 150 length).
