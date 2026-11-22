# Graph Report - obs_backup  (2026-11-22)

## Corpus Check
- 50 files · ~29,441 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 577 nodes · 1358 edges · 22 communities (19 shown, 3 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 84 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `77105ca4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- tr
- InstallPanel
- RestoreTab
- AppSettings
- Selection
- restore.py
- SelectionTree
- build.py
- test_i18n.py
- config.py
- locator.py
- test_manifest.py
- collect.py
- Backup Selection Checkbox Tree
- Backup & Restore for OBS
- test_locator.py
- _frozen
- backup-restore-for-obs
- GNU General Public License v2
- RELEASE_NOTES_TEMPLATE.md
- CLAUDE.md
- psutil BSD 3-Clause License

## God Nodes (most connected - your core abstractions)
1. `Selection` - 40 edges
2. `AppSettings` - 34 edges
3. `tr()` - 34 edges
4. `MainWindow` - 28 edges
5. `InstallPanel` - 24 edges
6. `TaskRunner` - 22 edges
7. `SelectionTree` - 20 edges
8. `RestoreTab` - 19 edges
9. `create_backup()` - 17 edges
10. `BackupTab` - 17 edges

## Surprising Connections (you probably didn't know these)
- `test_list_backups()` --calls--> `Selection`  [INFERRED]
  tests/backup/test_manifest.py → src/obs_backup/backup/models.py
- `test_list_backups_skips_damaged_manifests()` --calls--> `Selection`  [INFERRED]
  tests/backup/test_manifest.py → src/obs_backup/backup/models.py
- `test_everything_but_browser_data_is_ticked_by_default()` --uses--> `SelectionTree`  [INFERRED]
  tests/gui/test_selection_tree.py → src/obs_backup/gui/selection_tree.py
- `test_select_none_and_all()` --uses--> `SelectionTree`  [INFERRED]
  tests/gui/test_selection_tree.py → src/obs_backup/gui/selection_tree.py
- `test_empty_selection_rejected()` --calls--> `Selection`  [INFERRED]
  tests/backup/test_create.py → src/obs_backup/backup/models.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Selectable OBS Backup Categories** — docs_screenshot_profiles, docs_screenshot_scene_collections, docs_screenshot_general_settings, docs_screenshot_plugin_settings, docs_screenshot_browser_source_dock_data [EXTRACTED 1.00]
- **Backup Creation Flow (Source, Selection, Destination, Action)** — docs_screenshot_obs_installation_panel, docs_screenshot_backup_selection_tree, docs_screenshot_include_media_files, docs_screenshot_save_to_destination, docs_screenshot_create_backup_button [INFERRED 0.85]

## Communities (22 total, 3 thin omitted)

### Community 0 - "tr"
Cohesion: 0.07
Nodes (46): collections_abc, locale, pathlib, pyside6_qtcore, pyside6_qtgui, pyside6_qtwidgets, QDialog, QUrl (+38 more)

### Community 1 - "InstallPanel"
Cohesion: 0.07
Nodes (21): QGroupBox, QObject, BackupTab, Path, QWidget, Show the contents of the currently selected OBS config folder., InstallPanel, Path (+13 more)

### Community 2 - "RestoreTab"
Cohesion: 0.16
Nodes (10): Path, QWidget, List the backups in the backup folder; keep or set the selected one., Allow restoring only with a valid backup, OBS closed and no task running., RestoreTab, task(), FolderEdit, Path (+2 more)

### Community 3 - "AppSettings"
Cohesion: 0.08
Nodes (28): QApplication, QCloseEvent, QMainWindow, setter, MainWindow, Slot, Create menus and widgets in the current language (again after a language…, AppSettings (+20 more)

### Community 4 - "Selection"
Cohesion: 0.07
Nodes (63): io, json, MonkeyPatch, pytest, What to back up or restore., Selection, struct, _FailsHalfway (+55 more)

### Community 5 - "restore.py"
Cohesion: 0.05
Nodes (80): BaseException, dataclasses, datetime, Exception, os, platform, _add_complete_file(), _compression() (+72 more)

### Community 6 - "SelectionTree"
Cohesion: 0.14
Nodes (12): QTreeWidget, QTreeWidgetItem, _children(), QWidget, Profiles and scene collections as groups, the other items as single entries., Fill the tree. ``profiles`` and ``scenes`` are ``(display name, key)`` pairs., SelectionTree, fixture (+4 more)

### Community 7 - "build.py"
Cohesion: 0.06
Nodes (35): CI workflow, lint job (ruff format, ruff check, pyright), test job (pytest on Windows + Ubuntu matrix), build job (Windows exe / Linux tar.gz), Code signing (SignPath Foundation / OSSign), release job (draft GitHub release), Release workflow, SHA256SUMS.txt checksums (+27 more)

### Community 8 - "test_i18n.py"
Cohesion: 0.14
Nodes (16): run(), PySide6 user interface. - ``app``: start the application - ``main_window``:…, Language code for a locale name such as ``"de_DE"`` (default: the system…, system_language(), main(), Entry point: ``python -m obs_backup`` or the ``backup-restore-for-obs`` command., string, placeholders() (+8 more)

### Community 9 - "config.py"
Cohesion: 0.14
Nodes (23): ConfigParser, contextlib, itertools, full_selection(), What to back up before restoring ``restoring``: everything a restore can…, Everything worth keeping, except browser data (large, and rarely restored)., safety_selection(), _manifest() (+15 more)

### Community 10 - "locator.py"
Cohesion: 0.23
Nodes (20): psutil, config_dir_for_process(), default_config_dir(), discover(), add(), find_running_obs(), flatpak_config_dir(), _home() (+12 more)

### Community 11 - "test_manifest.py"
Cohesion: 0.18
Nodes (16): skipif, is_plain_name(), Layout of a backup file. A backup is a plain zip file:: manifest.json what the…, Whether ``name`` is one file or folder name on this OS, safe to join to a…, parametrize, Path, Reading manifests and listing backups., test_drive_relative_name_is_not_plain() (+8 more)

### Community 12 - "collect.py"
Cohesion: 0.12
Nodes (25): collect_files(), _is_browser_cache_dir(), _is_browser_skip_file(), Path, Work out which files a backup should contain., All files under ``root`` (or ``root`` itself if it is a file), sorted., Files under ``config_dir`` that ``sel`` covers (without media)., Media files the given scene collections use and that exist on this machine. (+17 more)

### Community 13 - "Backup Selection Checkbox Tree"
Cohesion: 0.16
Nodes (16): Backup Selection Checkbox Tree, Back up Tab, Browser Source & Dock Data (Cookies, Logins), Create Backup Button, General Settings (global.ini, user.ini, Plugin Manager), Include Media Files Used by Scenes Option, Language Menu (Localization), OBS Backup & Restore Main Window (Screenshot) (+8 more)

### Community 14 - "Backup & Restore for OBS"
Cohesion: 0.12
Nodes (15): AI disclosure, Backup file format, Backup & Restore for OBS, Contributing, Download, Features, License, Privacy (+7 more)

### Community 17 - "test_locator.py"
Cohesion: 0.29
Nodes (4): Path, Finding OBS and its config folder., test_portable_by_flag(), test_portable_by_marker_file()

### Community 18 - "_frozen"
Cohesion: 0.50
Nodes (4): frozendict, K, _frozen(), V

### Community 21 - "GNU General Public License v2"
Cohesion: 0.40
Nodes (6): GNU General Public License v3, GNU Lesser General Public License v3, PyInstaller Bootloader Exception, GNU General Public License v2, PyInstaller licensing terms, PyInstaller run-time hooks (Apache 2.0)

### Community 22 - "RELEASE_NOTES_TEMPLATE.md"
Cohesion: 0.50
Nodes (3): AI disclosure, Download, Licenses

## Knowledge Gaps
- **28 isolated node(s):** `backup-restore-for-obs`, `Download`, `AI disclosure`, `Licenses`, `graphify` (+23 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 190 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `tr()` connect `tr` to `InstallPanel`, `RestoreTab`, `AppSettings`, `SelectionTree`, `build.py`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `AppSettings` connect `AppSettings` to `tr`, `test_i18n.py`, `RestoreTab`, `InstallPanel`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `Selection` connect `Selection` to `tr`, `restore.py`, `SelectionTree`, `config.py`, `test_manifest.py`, `collect.py`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 29 inferred relationships involving `Selection` (e.g. with `collect_files()` and `safety_selection()`) actually correct?**
  _`Selection` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `AppSettings` (e.g. with `BackupTab` and `InstallPanel`) actually correct?**
  _`AppSettings` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `MainWindow` (e.g. with `BackupTab` and `InstallPanel`) actually correct?**
  _`MainWindow` has 13 INFERRED edges - model-reasoned connections that need verification._
- **What connects `backup-restore-for-obs`, `Download`, `AI disclosure` to the rest of the system?**
  _28 weakly-connected nodes found - possible documentation gaps or missing edges._