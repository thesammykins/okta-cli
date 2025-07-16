# Releasing Okta CLI

This document describes the release process for the Okta CLI tool.

## Release Types

- **Patch** (1.0.0 → 1.0.1): Bug fixes, security updates
- **Minor** (1.0.0 → 1.1.0): New features, backward compatible
- **Major** (1.0.0 → 2.0.0): Breaking changes

## Automated Release Process

### Using GitHub Actions (Recommended)

1. **Version Bump Workflow**:
   - Go to Actions → "Version Bump"
   - Click "Run workflow"
   - Select version type (patch/minor/major)
   - This creates a PR with version updates

2. **Release Workflow**:
   - Merge the version bump PR
   - Create a new release on GitHub with tag `v{version}`
   - The release workflow automatically:
     - Builds the package
     - Creates GitHub release with assets
     - Publishes to PyPI (if `PYPI_TOKEN` is set)
     - Builds Docker image

### Manual Release Process

1. **Using the Release Script**:
   ```bash
   ./scripts/release.sh
   ```

2. **Manual Steps**:
   ```bash
   # Run tests
   pytest tests/ -v
   
   # Bump version
   bump2version patch  # or minor/major
   
   # Build package
   python -m build
   
   # Push to remote
   git push
   git push --tags
   
   # Create GitHub release
   gh release create v1.0.1 --generate-notes
   ```

## GitHub Actions Workflows

### 1. CI Workflow (`.github/workflows/ci.yml`)
- **Triggers**: Push to main/develop branches, PRs
- **Tasks**: 
  - Run tests on multiple Python versions
  - Code linting and formatting checks
  - Security scanning
  - Build verification

### 2. Release Workflow (`.github/workflows/release.yml`)
- **Triggers**: Tag push (`v*.*.*`) or manual dispatch
- **Tasks**:
  - Multi-platform testing
  - Package building
  - GitHub release creation
  - PyPI publishing
  - Docker image creation

### 3. Version Bump Workflow (`.github/workflows/version-bump.yml`)
- **Triggers**: Manual dispatch
- **Tasks**:
  - Automated version bumping
  - Create PR with version changes

## Required Secrets

Set these in GitHub repository settings:

- `GITHUB_TOKEN`: Automatically provided by GitHub
- `PYPI_TOKEN`: PyPI API token for publishing (optional)

## Release Checklist

### Pre-release
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] No security vulnerabilities
- [ ] Code is formatted (black, flake8)

### Release
- [ ] Version is bumped appropriately
- [ ] Git tag is created
- [ ] GitHub release is created
- [ ] Package is built successfully
- [ ] PyPI upload successful (if applicable)
- [ ] Docker image is built

### Post-release
- [ ] Release notes are complete
- [ ] Documentation is published
- [ ] Community is notified
- [ ] Next version planning

## Version Management

The project uses [bump2version](https://github.com/c4urself/bump2version) for version management.

### Configuration
- `.bumpversion.cfg`: Configuration file
- `pyproject.toml`: Version in project metadata
- `okta_cli/__init__.py`: Version in code

### Commands
```bash
# Patch version (1.0.0 → 1.0.1)
bump2version patch

# Minor version (1.0.0 → 1.1.0)
bump2version minor

# Major version (1.0.0 → 2.0.0)
bump2version major
```

## Distribution

### PyPI
The package is automatically published to PyPI when:
- A new tag is pushed
- The release workflow runs successfully
- `PYPI_TOKEN` secret is configured

### Docker
Docker images are published to GitHub Container Registry:
- `ghcr.io/username/okta-cli:latest`
- `ghcr.io/username/okta-cli:v1.0.0`

### Manual Distribution
```bash
# Build package
python -m build

# Upload to PyPI
twine upload dist/*

# Build Docker image
docker build -t okta-cli:latest .
```

## Troubleshooting

### Common Issues

1. **Version bump fails**:
   - Check `.bumpversion.cfg` configuration
   - Ensure files are in sync
   - Verify git is clean

2. **PyPI upload fails**:
   - Check `PYPI_TOKEN` secret
   - Verify package name availability
   - Ensure proper permissions

3. **Docker build fails**:
   - Check Dockerfile syntax
   - Verify base image availability
   - Review build context

### Debug Commands
```bash
# Check current version
grep -E "^version = " pyproject.toml

# Test build
python -m build

# Verify package
pip install dist/*.whl
okta-cli --version

# Test Docker build
docker build -t okta-cli:test .
docker run okta-cli:test --version
```

## Best Practices

1. **Always test before release**
2. **Use semantic versioning**
3. **Write meaningful commit messages**
4. **Update documentation**
5. **Keep changelog current**
6. **Tag releases consistently**
7. **Monitor post-release issues**

## Support

For release issues:
1. Check GitHub Actions logs
2. Review workflow files
3. Verify repository settings
4. Check secret configurations
5. Contact maintainers if needed