# Graph Report - obs_backup  (2026-11-22)

## Corpus Check
- Corpus is ~26,303 words - fits in a single context window. You may not need a graph.

## Summary
- 500 nodes · 1156 edges · 21 communities (20 shown, 1 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 72 edges (avg confidence: 0.92)
- Token cost: 103,250 input · 0 output

## Community Hubs (Navigation)
- App Startup & About Box
- Backup Tab & OBS Panel
- CI, Release & Licensing Docs
- Main Window
- Backup & Restore Tests
- Backup Errors & Manifest
- Selection Tree
- Build Script & Licenses
- Restore Logic & Models
- OBS Config Reading
- OBS Locator
- App Settings & Restore Start
- Media Path Handling
- UI Screenshot Elements
- Backup Creation
- Backup File Collection
- Translation Tests
- Locator Tests
- frozendict Helper
- Config Tests
- Package Metadata

## God Nodes (most connected - your core abstractions)
1. `tr()` - 34 edges
2. `AppSettings` - 30 edges
3. `Selection` - 24 edges
4. `InstallPanel` - 24 edges
5. `MainWindow` - 24 edges
6. `TaskRunner` - 22 edges
7. `Backup & Restore for OBS` - 22 edges
8. `SelectionTree` - 20 edges
9. `RestoreTab` - 18 edges
10. `BackupTab` - 17 edges

## Surprising Connections (you probably didn't know these)
- `test_empty_selection_rejected()` --calls--> `Selection`  [INFERRED]
  tests/backup/test_create.py → src/obs_backup/backup/models.py
- `test_partial_selection()` --calls--> `Selection`  [INFERRED]
  tests/backup/test_create.py → src/obs_backup/backup/models.py
- `test_list_backups()` --calls--> `Selection`  [INFERRED]
  tests/backup/test_manifest.py → src/obs_backup/backup/models.py
- `test_rejects_zip_slip()` --calls--> `Selection`  [INFERRED]
  tests/backup/test_restore.py → src/obs_backup/backup/models.py
- `test_restore_only_selected()` --calls--> `Selection`  [INFERRED]
  tests/backup/test_restore.py → src/obs_backup/backup/models.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Third-party components bundled in the standalone apps** — third_party_notices_qt6, third_party_notices_pyside6, third_party_notices_psutil, third_party_notices_python_runtime, third_party_notices_pyinstaller_bootloader, third_party_notices_msvc_runtime [EXTRACTED 1.00]
- **Tagged release pipeline (version check, build, checksums, draft notes)** — _github_workflows_release_release_workflow, _github_workflows_release_build_job, _github_workflows_release_tag_version_check, _github_workflows_release_release_job, _github_workflows_release_sha256sums, _github_release_notes_template_release_notes_template, _github_release_notes_template_repo_url_placeholder [EXTRACTED 1.00]
- **Code quality toolchain (pre-commit, CI lint and tests)** — readme_ruff, readme_pyright, readme_pytest, _github_workflows_ci_lint_job, _github_workflows_ci_test_job, _pre_commit_config_ruff_check_hook, _pre_commit_config_ruff_format_hook [INFERRED 0.85]
- **Selectable OBS Backup Categories** — docs_screenshot_profiles, docs_screenshot_scene_collections, docs_screenshot_general_settings, docs_screenshot_plugin_settings, docs_screenshot_browser_source_dock_data [EXTRACTED 1.00]
- **Backup Creation Flow (Source, Selection, Destination, Action)** — docs_screenshot_obs_installation_panel, docs_screenshot_backup_selection_tree, docs_screenshot_include_media_files, docs_screenshot_save_to_destination, docs_screenshot_create_backup_button [INFERRED 0.85]

## Communities (21 total, 1 thin omitted)

### Community 0 - "App Startup & About Box"
Cohesion: 0.07
Nodes (44): collections_abc, locale, pathlib, pyside6_qtcore, pyside6_qtgui, pyside6_qtwidgets, QDialog, QUrl (+36 more)

### Community 1 - "Backup Tab & OBS Panel"
Cohesion: 0.05
Nodes (30): QGroupBox, QObject, BackupTab, Path, QWidget, Show the contents of the currently selected OBS config folder., InstallPanel, Path (+22 more)

### Community 2 - "CI, Release & Licensing Docs"
Cohesion: 0.07
Nodes (56): Release Notes Template, REPO_URL placeholder, Unsigned apps / SmartScreen warning, CI workflow, lint job (ruff format, ruff check, pyright), test job (pytest on Windows + Ubuntu matrix), build job (Windows exe / Linux tar.gz), Code signing (SignPath Foundation / OSSign) (+48 more)

### Community 3 - "Main Window"
Cohesion: 0.10
Nodes (20): QApplication, QCloseEvent, QMainWindow, open_folder(), Path, Show a folder in the system file manager., MainWindow, Slot (+12 more)

### Community 4 - "Backup & Restore Tests"
Cohesion: 0.13
Nodes (25): os, Path, test_backup_contents(), test_backup_without_browser_and_media(), test_empty_selection_rejected(), test_partial_selection(), Path, Restoring backups, including media remapping and unsafe archives. (+17 more)

### Community 5 - "Backup Errors & Manifest"
Cohesion: 0.15
Nodes (21): dataclasses, Exception, default_backup_name(), BackupError, InvalidBackupError, Errors raised while creating or restoring backups., A backup could not be created or restored., A file is not a valid backup, or is damaged or unsafe. (+13 more)

### Community 6 - "Selection Tree"
Cohesion: 0.10
Nodes (17): pytest, QTreeWidget, QTreeWidgetItem, _children(), QWidget, Profiles and scene collections as groups, the other items as single entries., Fill the tree. ``profiles`` and ``scenes`` are ``(display name, key)`` pairs., SelectionTree (+9 more)

### Community 7 - "Build Script & Licenses"
Cohesion: 0.12
Nodes (20): app_version(), copy_python_license(), main(), Path, Build the standalone app with PyInstaller. uv run python packaging/build.py…, Version resource (file properties → Details) for the Windows .exe., The license of the Python being bundled; it lists that build's own libraries.…, write_windows_version_info() (+12 more)

### Community 8 - "Restore Logic & Models"
Cohesion: 0.15
Nodes (20): Data passed into and returned from backup and restore., What to back up or restore., RestoreResult, Selection, _is_selected(), members_for(), _plan_media(), Path (+12 more)

### Community 9 - "OBS Config Reading"
Cohesion: 0.16
Nodes (20): ConfigParser, contextlib, itertools, full_selection(), Everything worth keeping, as used for the safety backup before a restore., _CaseKeepingParser, has_browser_data(), has_plugin_config() (+12 more)

### Community 10 - "OBS Locator"
Cohesion: 0.23
Nodes (20): psutil, config_dir_for_process(), default_config_dir(), discover(), add(), find_running_obs(), flatpak_config_dir(), _home() (+12 more)

### Community 11 - "App Settings & Restore Start"
Cohesion: 0.25
Nodes (6): setter, documents_dir(), task(), AppSettings, Path, Typed access to the app's QSettings (registry on Windows, a .conf file on…

### Community 12 - "Media Path Handling"
Cohesion: 0.18
Nodes (15): json, find_media_files(), iter_strings(), looks_like_local_path(), Any, Find and rewrite the local file paths that scene collections refer to. Sources…, Absolute paths of existing files referenced by a scene collection, as stored., replace_strings() (+7 more)

### Community 13 - "UI Screenshot Elements"
Cohesion: 0.16
Nodes (16): Backup Selection Checkbox Tree, Back up Tab, Browser Source & Dock Data (Cookies, Logins), Create Backup Button, General Settings (global.ini, user.ini, Plugin Manager), Include Media Files Used by Scenes Option, Language Menu (Localization), OBS Backup & Restore Main Window (Screenshot) (+8 more)

### Community 14 - "Backup Creation"
Cohesion: 0.18
Nodes (13): datetime, platform, _compression(), create_backup(), _manifest(), Path, Progress, Create a backup file. (+5 more)

### Community 15 - "Backup File Collection"
Cohesion: 0.19
Nodes (13): collect_files(), _is_browser_cache_dir(), _is_browser_skip_file(), Path, Work out which files a backup should contain., All files under ``root`` (or ``root`` itself if it is a file), sorted., Files under ``config_dir`` that ``sel`` covers (without media)., Media files the given scene collections use and that exist on this machine. (+5 more)

### Community 16 - "Translation Tests"
Cohesion: 0.25
Nodes (10): string, placeholders(), parametrize, Translations: complete, consistent and matching the texts the code uses., test_every_used_key_exists(), test_language_has_every_key(), test_no_unused_keys(), test_placeholders_match_english() (+2 more)

### Community 17 - "Locator Tests"
Cohesion: 0.29
Nodes (4): Path, Finding OBS and its config folder., test_portable_by_flag(), test_portable_by_marker_file()

### Community 18 - "frozendict Helper"
Cohesion: 0.50
Nodes (4): frozendict, K, _frozen(), V

### Community 19 - "Config Tests"
Cohesion: 0.50
Nodes (3): Path, Reading profiles, scene collections and the OBS version., test_reads_config()

## Ambiguous Edges - Review These
- `Code signing (SignPath Foundation / OSSign)` → `Privacy: no telemetry, no update check, no accounts`  [AMBIGUOUS]
  README.md · relation: conceptually_related_to

## Knowledge Gaps
- **11 isolated node(s):** `backup-restore-for-obs`, `App settings storage (registry / ~/.config)`, `Python 3.15 (lazy imports, frozendict)`, `pyright (type checker behind Pylance)`, `Adding a UI language (i18n _MODULES)` (+6 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 145 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Code signing (SignPath Foundation / OSSign)` and `Privacy: no telemetry, no update check, no accounts`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Run from source` connect `CI, Release & Licensing Docs` to `Build Script & Licenses`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Why does `tr()` connect `App Startup & About Box` to `App Settings & Restore Start`, `Backup Tab & OBS Panel`, `Main Window`, `Selection Tree`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Why does `AppSettings` connect `App Settings & Restore Start` to `App Startup & About Box`, `Backup Tab & OBS Panel`, `Main Window`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `AppSettings` (e.g. with `BackupTab` and `InstallPanel`) actually correct?**
  _`AppSettings` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `Selection` (e.g. with `collect_files()` and `create_backup()`) actually correct?**
  _`Selection` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `InstallPanel` (e.g. with `BackupTab` and `AppSettings`) actually correct?**
  _`InstallPanel` has 6 INFERRED edges - model-reasoned connections that need verification._