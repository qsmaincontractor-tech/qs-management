Release checklist

1. Ensure all tests pass locally: `python -m pytest -q "04 QS Management/tests"`
2. Build artifacts: `python -m build "04 QS Management"`
3. Commit and tag: `git tag -a v0.9.0b1 -m "Beta release 0.9.0b1"`
4. Push tag: `git push origin --tags`
5. Draft a GitHub release and attach the files from `04 QS Management/dist/`.
6. Update PyPI (optional) using `twine upload dist/*` after creating an account and API token.

Be sure to update `CHANGELOG.md` and `README.md` with any last-minute notes.
