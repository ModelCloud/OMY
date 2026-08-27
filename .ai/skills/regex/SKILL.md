---
name: regex-usage
description: Rules for using regular expressions in the OMY repository.
---

# Regular expressions in OMY

OMY standardizes all regular expression usage on `pypcre`, a PCRE2-based regex engine that is GIL-friendly and thread-safe.

## Dependency

- PyPI package name: `PyPcre`
- Minimum version: `>=0.6.2`
- Python import package: `pcre`

## Rule: never use `re` or `regex` directly

Always import `pcre` and, when needed for compatibility with existing call sites, alias it as `re`:

```python
import pcre as re
```

Do **not** use `import re` (stdlib) or `import regex` (third-party).

## API compatibility

`pcre` mirrors the standard `re` API:

- `pcre.compile`, `pcre.search`, `pcre.match`, `pcre.fullmatch`, `pcre.findall`, `pcre.finditer`
- `pcre.split`, `pcre.sub`, `pcre.subn`, `pcre.escape`, `pcre.template`
- `pcre.error`, `pcre.I`, `pcre.M`, `pcre.S`, `pcre.X`, `pcre.VERBOSE`, `pcre.UNICODE`, and other flag aliases

## Type-checker friendly flags

At runtime `pcre` exposes stdlib-style flag aliases (e.g. `re.DOTALL`, `re.IGNORECASE`, `re.VERBOSE`, `re.MULTILINE`).
For the static `ty` checker, refer to constants through `pcre.Flag`:

- `re.DOTALL` / `re.S` → `re.Flag.DOTALL`
- `re.MULTILINE` / `re.M` → `re.Flag.MULTILINE`
- `re.IGNORECASE` / `re.I` → `re.Flag.CASELESS`
- `re.VERBOSE` / `re.X` → `re.Flag.EXTENDED`

## Important implementation differences

- `pcre.Pattern` and `pcre.Match` are C extension classes and are **not generic**.
  - Do not use `re.Pattern[str]` or `re.Match[str]`; use `re.Pattern` and `re.Match` instead.
- `pcre.Pattern` objects are **not pickleable**.
  - `copy.copy(pattern)` works, but `copy.deepcopy(pattern)` and `pickle` do not.
  - If a class holds compiled patterns and is deep-copied, implement `__deepcopy__` to copy the compiled pattern with `copy.copy` while deep-copying the rest.

## Example

```python
import pcre as re

pattern = re.compile(r"\d+", re.Flag.CASELESS)
match = pattern.search("abc 123")
```
