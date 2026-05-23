# Daily Reflections Mode

## Overview

A display mode that shows one reflection question per day. Uses deterministic randomness (date as seed) so the same day always shows the same reflection, and a new day selects a different one.

## Components

### 1. ReflectionsMode (`sweets/modes/reflections.py`)

**Class attributes:**
- `name = "Daily Reflections"`
- `slug = "reflections"`
- `interval = 3600` (check every hour)

**Behavior:**
- Load reflections from `reflections.yaml` in project root
- If file missing or empty: render "ADD REFLECTIONS" placeholder
- Use `datetime.date.today()` to seed a `random.Random()` instance
- Select reflection at index `rng.randrange(len(reflections))`
- Use `Board.from_text()` to word-wrap and center the text

### 2. Reflections file (`reflections.yaml`)

YAML list at project root. User populates manually.

```yaml
- "What are you grateful for?"
- "What did you learn today?"
```

### 3. Tests (`tests/modes/test_reflections.py`)

- Same date seed produces same reflection
- Different dates produce different selections (probabilistic)
- Missing file shows "ADD REFLECTIONS"
- Empty file shows "ADD REFLECTIONS"
- Single reflection always returns that reflection

## Implementation Notes

- No persistent state file needed
- Deterministic: `random.Random(date.toordinal())` ensures reproducibility
- Auto-discovered by existing registry system
