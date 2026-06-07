# Changelog

## [1.7.0](https://github.com/travipross/new-brunswick-burn-ban-status/compare/v1.6.0...v1.7.0) (2026-06-07)


### Features

* rename integration to New BURNswick - NB Fire Watch ([0b0ca1a](https://github.com/travipross/new-brunswick-burn-ban-status/commit/0b0ca1a3ff80b5ab31d4f5193bf9bdb12b5b8704))


### Documentation

* move development guidelines and technical logic to CONTRIBUTING.md ([e94978c](https://github.com/travipross/new-brunswick-burn-ban-status/commit/e94978c35aebca07a9314c4cca760d969a5f7299))
* update license and add HACS repository 'My Link' shortcut ([4e9d74c](https://github.com/travipross/new-brunswick-burn-ban-status/commit/4e9d74cb53e1a7614df618490c6a51f2e3e0e284))
* update README with new title and status badges ([839418e](https://github.com/travipross/new-brunswick-burn-ban-status/commit/839418e4dce11523cc82af8da8777ac9e9405ac8))

## [1.6.0](https://github.com/travipross/new-brunswick-burn-ban-status/compare/v1.5.2...v1.6.0) (2026-06-07)


### Chores

* fix validation errors for HACS and Hassfest ([021593d](https://github.com/travipross/new-brunswick-burn-ban-status/commit/021593d))
* prepare integration for HACS default publication ([44af720](https://github.com/travipross/new-brunswick-burn-ban-status/commit/44af720))

## [1.5.2](https://github.com/travipross/new-brunswick-burn-ban-status/compare/v1.5.1...v1.5.2) (2026-06-07)


### Features

* align polling logic with 2 PM Atlantic synchronization window ([f4fd5b6](https://github.com/travipross/new-brunswick-burn-ban-status/commit/f4fd5b6))

## [1.5.1](https://github.com/travipross/new-brunswick-burn-ban-status/compare/v1.5.0...v1.5.1) (2026-06-05)


### Bug Fixes

* provide entity name for county-specific burn category sensor ([c471142](https://github.com/travipross/new-brunswick-burn-ban-status/commit/c471142))

## [1.5.0](https://github.com/travipross/new-brunswick-burn-ban-status/compare/v1.4.3...v1.5.0) (2026-06-05)


### Features

* add raw API attributes and document update logic ([3ef6e5c](https://github.com/travipross/new-brunswick-burn-ban-status/commit/3ef6e5c))


### Code Refactoring

* centralize identifiers for robust registry cleanup ([3deb890](https://github.com/travipross/new-brunswick-burn-ban-status/commit/3deb890))
* simplify device and entity naming for better UI clarity ([ad69e11](https://github.com/travipross/new-brunswick-burn-ban-status/commit/ad69e11))

## [1.4.3](https://github.com/travipross/new-brunswick-burn-ban-status/compare/v1.4.2...v1.4.3) (2026-06-01)


### Bug Fixes

* correct device and entity registry cleanup identifiers ([03f49b6](https://github.com/travipross/new-brunswick-burn-ban-status/commit/03f49b6))

## [1.4.2](https://github.com/travipross/new-brunswick-burn-ban-status/compare/v1.4.1...v1.4.2) (2026-06-01)


### Code Refactoring

* rename and further consolidate device naming ([b315dd8](https://github.com/travipross/new-brunswick-burn-ban-status/commit/b315dd8))

## [1.4.1](https://github.com/travipross/new-brunswick-burn-ban-status/compare/v1.4.0...v1.4.1) (2026-06-01)


### Code Refactoring

* consolidate sensor under common device/service ([aeccda3](https://github.com/travipross/new-brunswick-burn-ban-status/commit/aeccda3))

## [1.4.0](https://github.com/travipross/new-brunswick-burn-ban-status/compare/v1.3.3...v1.4.0) (2026-06-01)


### Features

* add diagnostic sensor for next update time ([3dd726a](https://github.com/travipross/new-brunswick-burn-ban-status/commit/3dd726a))


### Code Refactoring

* simplify mocks, improve polling logging, and expand tests ([a79a2b8](https://github.com/travipross/new-brunswick-burn-ban-status/commit/a79a2b8))

## [1.3.3](https://github.com/travipross/new-brunswick-burn-ban-status/compare/v1.3.2...v1.3.3) (2026-06-01)


### Bug Fixes

* improve polling logic robustness using VALIDDATE timestamp ([96d6d97](https://github.com/travipross/new-brunswick-burn-ban-status/commit/96d6d97))

## [1.3.2](https://github.com/travipross/new-brunswick-burn-ban-status/compare/v1.3.1...v1.3.2) (2026-05-31)


### Bug Fixes

* update image entity logic for cache-busting again ([56e7276](https://github.com/travipross/new-brunswick-burn-ban-status/commit/56e7276))


### Development

* add dependencies and update gitignore ([c609579](https://github.com/travipross/new-brunswick-burn-ban-status/commit/c609579))

## [1.3.1](https://github.com/travipross/new-brunswick-burn-ban-status/compare/v1.3.0...v1.3.1) (2026-05-26)


### Bug Fixes

* avoid options flow config_entry assignment ([b5dd7b5](https://github.com/travipross/new-brunswick-burn-ban-status/commit/b5dd7b5))


### Tests

* add options flow regression for read-only config_entry ([78c4726](https://github.com/travipross/new-brunswick-burn-ban-status/commit/78c4726))

## [1.3.0](https://github.com/travipross/new-brunswick-burn-ban-status/compare/v1.2.4...v1.3.0) (2026-05-26)


### Features

* allow empty county selection and improve setup resilience ([45446ed](https://github.com/travipross/new-brunswick-burn-ban-status/commit/45446ed))


### Code Refactoring

* **cleanup:** centralize registry cleanup for devices and entities ([b538fe1](https://github.com/travipross/new-brunswick-burn-ban-status/commit/b538fe1))
* implement typing and dead code cleanup ([5e603d5](https://github.com/travipross/new-brunswick-burn-ban-status/commit/5e603d5))


### Chores

* add conventional commit mandate to agent instructions ([a96238e](https://github.com/travipross/new-brunswick-burn-ban-status/commit/a96238e))
* establish quality baseline with linting, testing, and CI ([cbcff0c](https://github.com/travipross/new-brunswick-burn-ban-status/commit/cbcff0c))


### Continuous Integration

* split quality checks into parallel jobs ([704b466](https://github.com/travipross/new-brunswick-burn-ban-status/commit/704b466))

## [1.2.4](https://github.com/travipross/new-brunswick-burn-ban-status/compare/v1.2.3...v1.2.4) (2026-05-25)


### Bug Fixes

* correct shifted date attributes in sensor entities ([9303d7a](https://github.com/travipross/new-brunswick-burn-ban-status/commit/9303d7a))

## [1.2.3](https://github.com/travipross/new-brunswick-burn-ban-status/compare/v1.2.2...v1.2.3) (2026-05-25)


### Bug Fixes

* update image entity logic for cache-busting ([3fb0945](https://github.com/travipross/new-brunswick-burn-ban-status/commit/3fb0945))

## [1.2.2](https://github.com/travipross/new-brunswick-burn-ban-status/compare/v1.2.1...v1.2.2) (2026-05-23)


### Bug Fixes

* remove query param from image ([f2c1d8a](https://github.com/travipross/new-brunswick-burn-ban-status/commit/f2c1d8a))

## [1.2.1](https://github.com/travipross/new-brunswick-burn-ban-status/compare/v1.2.0...v1.2.1) (2026-05-23)


### Bug Fixes

* fix missing import and add extra sensor attributes ([a7de47f](https://github.com/travipross/new-brunswick-burn-ban-status/commit/a7de47f))

## [1.2.0](https://github.com/travipross/new-brunswick-burn-ban-status/compare/v1.1.1...v1.2.0) (2026-05-23)


### Features

* add status_rgb attribute to sensor entities for easier automation with RGB bulbs ([1498bd1](https://github.com/travipross/new-brunswick-burn-ban-status/commit/1498bd1))
* optimize polling schedule and refine state transitions ([c99dc23](https://github.com/travipross/new-brunswick-burn-ban-status/commit/c99dc23))


### Chores

* add comprehensive debug logging for polling and transitions ([3a46a6a](https://github.com/travipross/new-brunswick-burn-ban-status/commit/3a46a6a))

## [1.1.1](https://github.com/travipross/new-brunswick-burn-ban-status/releases/tag/v1.1.1) (2026-05-23)


### Features

* add button to force refresh data ([673ae14](https://github.com/travipross/new-brunswick-burn-ban-status/commit/673ae14))
* perform cleanup on orphaned entities/devices ([79147ff](https://github.com/travipross/new-brunswick-burn-ban-status/commit/79147ff))


### Continuous Integration

* add release workflow ([df05955](https://github.com/travipross/new-brunswick-burn-ban-status/commit/df05955))


### Miscellaneous

* initial commit ([294f51e](https://github.com/travipross/new-brunswick-burn-ban-status/commit/294f51e))
