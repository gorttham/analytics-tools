# Analytics Toolkit — Standing Rules

## Data Handling
- Always validate that input is a pandas DataFrame before processing; raise a clear TypeError if not
- Never mutate the caller's DataFrame in-place — return a new one or an explicit copy
- Log column names and dtypes at the start of any profiling or cleaning function

## Code Style
- Functions must accept a DataFrame and return a result — no side-effect-only functions in `analytics/`
- Prefer explicit column selection over `df.select_dtypes()` magic where the intent isn't obvious
- All public functions in `analytics/` must have a docstring with Args, Returns, and Raises sections

## Testing
- Tests live in `tests/` mirroring the module structure (e.g. `tests/profiling/test_profiler.py`)
- Use real DataFrames in tests — do not mock pandas internals
- Each function must have at least one test for the happy path and one for invalid input
