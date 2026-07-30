# Atlas Quant v1.0.0 Release Checklist

## Pre-Release
- [ ] All tests pass (pytest --cov)
- [ ] Code coverage >= 80%
- [ ] mypy strict mode passes
- [ ] Ruff lint passes
- [ ] No known critical bugs
- [ ] CHANGELOG.md updated
- [ ] Version bumped to 1.0.0

## Build
- [ ] Docker build succeeds (backend)
- [ ] Docker build succeeds (frontend)
- [ ] docker-compose up works
- [ ] Database migration runs

## Deploy
- [ ] Production environment configured
- [ ] Database migrated
- [ ] API health check passes
- [ ] Frontend loads correctly
- [ ] Disclaimer headers present on all API responses

## Post-Release
- [ ] Git tag created (v1.0.0)
- [ ] GitHub Release created
- [ ] Release notes published
