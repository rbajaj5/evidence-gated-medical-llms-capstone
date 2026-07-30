# Release Notes: v0.2 Test Automation

Repository testing and public reproducibility polish.

## Added

- GitHub Actions workflow for `pytest` on push and pull request.
- Root `pytest.ini` so local and CI test entrypoints match.
- Package integrity tests for the final capstone directory and ZIP archive.

## Validation

Local validation before push:

```text
115 passed
```

## Boundary

No clinical behavior changed. The added tests only verify reproducibility and package integrity.
