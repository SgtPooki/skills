# Refactor triggers: extend or restructure?

The single decision SlopCodeBench showed agents getting wrong is the one at
the *start* of each iteration, not the end: when a new requirement arrives,
the minimal-diff move (add a flag, add a branch, paste a variant) is almost
always available and almost always wrong after the second time. This file
gives concrete triggers for choosing to restructure first.

## Triggers that mean "restructure before adding"

### 1. The requirement breaks a structural assumption

Signs: you find yourself adding a parameter that changes what a function
fundamentally does; an `is_x` boolean threading through several calls; a
branch near the top of a long function that shadows most of its body.

The assumption was baked in when N=1. Now N=2. The fix is to name the
abstraction the requirement revealed, not to special-case it.

**Before (extend — wrong after the 2nd language):**
```python
def search(pattern, path, lang="python"):
    if lang == "python":
        tree = py_parse(path)
        ...30 lines...
    elif lang == "javascript":
        tree = js_parse(path)
        ...28 nearly identical lines...
```

**After (restructure):**
```python
LANGUAGES = {"python": PythonLang(), "javascript": JsLang()}

def search(pattern, path, lang="python"):
    return LANGUAGES[lang].search(pattern, path)
```
Adding Go later is now one class + one dict entry — the exact scenario where
the benchmark watched agents do cascading rewrites instead.

### 2. This is the second (or third) variant of existing logic

If you are about to copy a block and tweak it, stop. Two occurrences is the
cheapest moment to extract: name the shared function, make the differences
parameters. At three-plus occurrences, extraction cost grows and every bug
now needs fixing in N places.

Corollary for CLI/config handling: the second `--flag` handled by an `if` in
`main()` means you need a real argument-dispatch structure, because flags
only ever accumulate. The study's flagship example is a `main()` that grew
38 → 240 lines, CCN ×7, purely from flags grafted into identical branches.

### 3. A function you are about to edit is already flagged

If slopcheck lists the function you're editing as high-complexity, apply the
boy-scout rule *before* adding your change: extract the piece you need to
touch into a helper, then modify the helper. Editing inside a CCN-25
function makes your change harder to verify AND pushes the function past the
gate.

### 4. You cannot summarize the function's job in one sentence

...without using "and". "Parses args and validates config and dispatches and
formats errors" is four functions wearing a trenchcoat.

## When extending IS right

Restructuring has costs (churn, review noise, risk) — this skill is not a
mandate to gold-plate. Extend directly when:

- The new case genuinely fits the existing structure (adding an entry to an
  existing dispatch table, a new subclass of an existing interface).
- The requirement is a leaf: it touches one place and creates no second
  variant of anything.
- You'd be building speculative generality — an abstraction for a variation
  that has exactly one instance and no concrete second one on the horizon.
  (Over-abstraction is also slop; it shows up as verbosity.)

The test: after your change, would a newcomer reading the code see one
coherent design, or see geological layers of requirements in the order they
arrived?

## Refactor mechanics under iteration

- Refactor and feature-add in **separate steps**: restructure with tests
  green, confirm green, then add the feature. Interleaving both is how you
  lose the thread and revert to minimal-diff mode.
- Extraction is the workhorse: named helper functions with the varying part
  as parameters beat clever metaprogramming. Optimize for the *next* edit
  being obvious.
- After removing a requirement or changing one, actively delete the code
  that served the old version. Agents leave fossils; humans running
  `slopcheck check` will find them as duplication/dead weight.
