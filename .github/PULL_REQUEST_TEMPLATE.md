## Summary

Describe the change and why it is needed.

## Related Issues

Link the issue this PR closes or relates to.

- Closes #

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Infrastructure or deployment change
- [ ] Refactor or maintenance

## Testing

List the checks you ran and their results.

```text
ruff check tools/
python3 tools/validate.py
python3 tools/generate.py
terraform validate
```

## Verification Notes

Describe any manual verification steps, deployment tests, or limitations.

## Checklist

- [ ] I followed the contribution guidelines in `CONTRIBUTING.md`
- [ ] I kept the change scoped to a single concern
- [ ] I updated docs or examples when user-facing behavior changed
- [ ] I added tests or documented why tests were not added
- [ ] I redacted secrets from logs, configs, and screenshots