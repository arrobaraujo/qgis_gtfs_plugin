# Changelog

## [1.1.6] - 2026-04-10
### Fixed
- **Code Quality**: Refactored statistics calculation to satisfy contradictory Flake8 line break rules.

## [1.1.5] - 2026-04-10
### Fixed
- **Code Quality**: Fixed Flake8 issues (E302 and W504) for full CI compliance.

## [1.1.4] - 2026-04-10
### Added
- **Authentication**: Updated the release workflow to use token-based authentication (Bearer JWT) for the official QGIS Repository.

## [1.1.3] - 2026-04-09
### Fixed
- **Bandit Audit**: Added security markers for URL processing to satisfy professional scanners.
- **Code Quality**: Resolved all remaining Flake8 violations (unused imports, redundant code, and formatting) across the core modules.
- **Lazy Imports**: Consolidated tracker initialization logic for better stability.

## [1.1.2] - 2026-04-09
### Fixed
- **QgsField Deprecation**: Resolved numerous warnings by centralizing field creation in `core/utils.py` with modern `QMetaType` and backward compatibility.
- **Protobuf Warnings**: Silenced deprecation warnings from legacy generated Protobuf code.
- **RT Manager Robustness**: Fixed a bug where switching feeds (URLs) in the UI did not update the tracker.
- **Layer Recovery**: Added auto-recovery for the real-time layer; the plugin now automatically recreates the layer if it was deleted by the user.
### Security
- **URL Validation**: Implemented strict scheme validation for GTFS-RT URLs (allowing only `http` and `https`) to prevent Local File Inclusion (B310).
### Improved
- **Code Quality**: Resolved 54+ PEP 8 violations across core modules for better maintainability and professional standards.

## [1.1.1] - 2026-04-09
### Added
- **Default GTFS-RT URL**: Set default feed link for Belo Horizonte (Mobilibus).
### Improved
- **Directional Vehicle Icons**: Replaced generic bus icons with bearing-based triangle indicators for clearer real-time visualization.

## [1.1.0] - 2026-04-09
### Added
- **GTFS-Realtime Tracking**: Integrate Google Protobuf feeds for live vehicle visualization.
- **Auto-Refresh**: Live memory layer that updates based on a configurable interval.
- **Dynamic Symbology**: Realistic vehicle icons that rotate based on the `bearing` field.
- **Dependency Management**: Automated installation of the `protobuf` library directly from the QGIS interface.
- **Feed Customization**: Allow users to define custom GTFS-RT URLs directly in the QGIS dashboard.
- **Performance**: Lazy loading of RT components for better plugin stability.

## [1.0.0] - 2026-04-01
- First stable `1.0.0` release.
- Updated plugin metadata version to `1.0.0`.
- Updated README and README.pt-BR version badges/headings to `1.0.0`.
- Fixed `QgsField` deprecation warnings by centralizing memory-layer field creation with a modern type path and compatibility fallback.

## [0.4.10] - 2026-04-01
- Corrected plugin compatibility policy to cap at `qgisMaximumVersion=4.0`.
- Updated README and README.pt-BR badges/text to reflect support range `3.40-4.0`.
- Fixed `QgsField` deprecation warnings by centralizing memory-layer field creation with a modern type path and compatibility fallback.

## [0.4.9] - 2026-04-01
- Added QGIS 4 compatibility metadata and set `qgisMaximumVersion=4.99`.
- Fixed Qt6 dialog execution compatibility by using `exec()` with fallback to `exec_()`.
- Fixed Qt6 type compatibility in memory layer fields by replacing `QMetaType.*` with `QVariant.*`.
- Fixed Qt6 enum compatibility for `NoPen`, `RightDockWidgetArea`, dialog button flags, and horizontal orientation.
- Fixed Qt6 UI loading issue by defining explicit spacer `sizeHint` in `ui/search_panel.ui`.
- Improved `clear_filters()` robustness for GTFS layers.
- Updated architecture and README files to document QGIS 3.40-4.x support.

## [0.4.8] - 2026-04-01
- Marked plugin as stable for QGIS repository publication (`experimental=False`).
- Bumped plugin version metadata to `0.4.8`.
- Updated English and Portuguese README version badges and headings.

## [0.4.7] - 2026-03-24
- Emergency fix: Restored `processor.py` and `search_panel.py` content and finalized PEP8 compliance across all core modules.

## [0.4.6] - 2026-03-24
- Extended PEP8 compliance: Resolved all styling issues in `processor.py` and `search_panel.py`, including unused imports and ambiguous variable names.

## [0.4.5] - 2026-03-24
- Absolute zero-tolerance PEP8 fix for `layer_factory.py`: Fixed hidden whitespaces, multi-statement exceptions, and restored accidentally truncated processing logic.

## [0.4.4] - 2026-03-24
- Surgical code style refactor: Resolved all 54 remaining PEP8 violations in `layer_factory.py`. Fixes include hidden whitespaces, single-line conditionals, and unused variables.

## [0.4.3] - 2026-03-24
- Absolute PEP8 compliance in `layer_factory.py`: Resolved remaining 86 styling issues (E261, E127, E701, E303, W291/W293).

## [0.4.2] - 2026-03-24
- Exhaustive code style refactor: Resolved 120+ PEP8 violations in `layer_factory.py` (whitespace, indentation, and structure).

## [0.4.1] - 2026-03-24
- CI/CD Fix: Used direct secret injection in `publish.yml` to ensure credential passing.

## [0.4.0] - 2026-03-24
- CI/CD Fix: Added explicit OSGeo server URL to `publish.yml`.
- Global code quality audit: Applied PEP8 compliance to all `.py` files.
- Refactored `processor.py`, `search_panel.py`, and `plugin.py`.

## [0.3.9] - 2026-03-24
- Rounded `shape_ext` values to integers as requested.

## [0.3.7] - 2026-03-24

## [0.3.6] - 2026-03-24

## [0.3.5] - 2026-03-24

## [0.3.4] - 2026-03-24

## [0.3.3] - 2026-03-24

## [0.3.2] - 2026-03-24

## [0.3.1] - 2026-03-24

## [0.3.0] - 2026-03-24 (Internal/Failed)
- Final fix for publication workflow and project structure.
- Unique version for official QGIS repository submission.
- Standardized documentation for global distribution.

## [0.2.8] - 2026-03-24
- Complete project restructuring for QGIS official repository standards.
- Fixed packaging error (ZIP now contains the plugin subdirectory).
- Fixed automated GitHub Release creation.

## [0.2.7] - 2026-03-24
- Updated metadata and fixed initial publication flow.
- First stable version for official repository.

## [0.2.6] - 2026-03-24
- Updated metadata and fixed initial publication flow.
- First stable version for official repository.
