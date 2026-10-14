# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

- `image-convergence` skill bundle (`skill/image-convergence/SKILL.md`): autonomous review-and-iterate loop for generated images with weakest-dimension scoring, stall detection with a six-tactic creative menu, and positive-only phrasing.
- `engine/image_convergence.py`: executable reference of the loop decision rule.
- Test suite (31 tests): decision tests over the engine, structural tests over the skill prose (threshold mirroring, positive-phrasing audit, agnosticism guard).
- Two-stage pipeline: `scripts/staging/{deploy.sh,e2e.sh,teardown.sh}` installing the bundle into a filesystem skills directory with branch-scoped staging.
