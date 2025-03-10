# Versioning Policy for NEURON Project

This document describes the versioning policy for the NEURON project, following the principles of [Semantic Versioning 2.0.0](https://semver.org/).

## Version Format

NEURON versions follow the `MAJOR.MINOR.PATCH` format where:

1. **MAJOR**: Incremented when making incompatible changes to the public API.
2. **MINOR**: Incremented when adding functionality in a backward-compatible manner.
3. **PATCH**: Incremented when making backward-compatible bug fixes.

## Rules

- We increment the **MAJOR** version number when we make incompatible changes to the public API.
- We increment the **MINOR** version number when we add functionality while maintaining compatibility with previous versions.
- We increment the **PATCH** version number when we make bug fixes while maintaining compatibility with previous versions.
- Versions with numbering 0.y.z are considered in initial development and may have changes at any time.

## Pre-release Versioning

For pre-release versions, we use suffixes following the format:

- `alpha`: Initial versions for internal testing
- `beta`: Versions for testing by selected external users
- `rc`: Release candidates, ready for final testing

Example: `1.0.0-alpha.1`, `1.0.0-beta.2`, `1.0.0-rc.1`

## Release Process

1. **Preparation**: 
   - Update CHANGELOG.md with changes for the new version
   - Update the version in the `pyproject.toml` file

2. **Testing**:
   - Run all automated tests
   - Perform manual tests to verify that the version is ready

3. **Release**:
   - Create a Git tag for the version (e.g., `v1.0.0`)
   - Merge to the main branch
   - Publish the package to relevant repositories

4. **Announcement**:
   - Announce the release in appropriate channels
   - Highlight the main changes and improvements

## Updating the Version

To update the project version:

1. Modify the `version` field in the `pyproject.toml` file
2. Update CHANGELOG.md with detailed changes
3. Create a commit with the message `release: bump version to vX.Y.Z`
4. Create a Git tag: `git tag vX.Y.Z`
5. Push the changes and tag to the remote repository 