# Graph Report - obs_backup  (2026-11-22)

## Corpus Check
- 51 files · ~31,291 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 649 nodes · 1556 edges · 28 communities (24 shown, 4 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 107 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dfcd05e3`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- tr
- TaskRunner
- RestoreTab
- AppSettings
- Selection
- backup/__init__.py
- SelectionTree
- build.py
- test_i18n.py
- config.py
- InstallPanel
- layout.py
- media.py
- Backup Selection Checkbox Tree
- Backup & Restore for OBS
- restore.py
- create.py
- manifest.py
- _frozen
- BackupTab
- backup-restore-for-obs
- GNU General Public License v2
- RELEASE_NOTES_TEMPLATE.md
- test_create.py
- CLAUDE.md
- psutil BSD 3-Clause License
- members_for
- .__init__

## God Nodes (most connected - your core abstractions)
1. `Selection` - 49 edges
2. `tr()` - 36 edges
3. `AppSettings` - 34 edges
4. `MainWindow` - 32 edges
5. `TaskRunner` - 26 edges
6. `InstallPanel` - 25 edges
7. `RestoreTab` - 22 edges
8. `SelectionTree` - 20 edges
9. `craft_backup()` - 20 edges
10. `create_backup()` - 18 edges

## Surprising Connections (you probably didn't know these)
- `test_empty_selection_rejected()` --calls--> `Selection`  [INFERRED]
  tests/backup/test_create.py → src/obs_backup/backup/models.py
- `test_file_dated_before_1980_is_backed_up()` --calls--> `Selection`  [INFERRED]
  tests/backup/test_create.py → src/obs_backup/backup/models.py
- `test_file_failing_halfway_is_left_out()` --calls--> `Selection`  [INFERRED]
  tests/backup/test_create.py → src/obs_backup/backup/models.py
- `test_partial_selection()` --calls--> `Selection`  [INFERRED]
  tests/backup/test_create.py → src/obs_backup/backup/models.py
- `test_language_change_replaces_the_menus()` --uses--> `MainWindow`  [INFERRED]
  tests/gui/test_main_window.py → src/obs_backup/gui/main_window.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Selectable OBS Backup Categories** — docs_screenshot_profiles, docs_screenshot_scene_collections, docs_screenshot_general_settings, docs_screenshot_plugin_settings, docs_screenshot_browser_source_dock_data [EXTRACTED 1.00]
- **Backup Creation Flow (Source, Selection, Destination, Action)** — docs_screenshot_obs_installation_panel, docs_screenshot_backup_selection_tree, docs_screenshot_include_media_files, docs_screenshot_save_to_destination, docs_screenshot_create_backup_button [INFERRED 0.85]

## Communities (28 total, 4 thin omitted)

### Community 0 - "tr"
Cohesion: 0.06
Nodes (50): collections_abc, html, locale, pathlib, pyside6_qtcore, pyside6_qtgui, pyside6_qtwidgets, QDialog (+42 more)

### Community 1 - "TaskRunner"
Cohesion: 0.12
Nodes (19): QObject, Any, Slot, Runs one task in the thread it is moved to., Runs one task at a time and reports its progress in the GUI thread., Start ``fn(progress)`` in the background. Afterwards ``on_done(result)`` runs,…, TaskRunner, Worker (+11 more)

### Community 2 - "RestoreTab"
Cohesion: 0.20
Nodes (6): Path, QWidget, List the backups in the backup folder; keep or set the selected one., Allow restoring only with a valid backup, OBS closed and no task running., RestoreTab, task()

### Community 3 - "AppSettings"
Cohesion: 0.08
Nodes (31): QCloseEvent, QMainWindow, setter, MainWindow, Slot, Create menus and widgets in the current language (again after a language…, AppSettings, Path (+23 more)

### Community 4 - "Selection"
Cohesion: 0.06
Nodes (81): json, os, skipif, What to back up or restore., Selection, struct, MonkeyPatch, parametrize (+73 more)

### Community 5 - "backup/__init__.py"
Cohesion: 0.13
Nodes (20): dataclasses, Exception, What to back up before restoring ``restoring``: everything a restore can…, safety_selection(), default_backup_name(), BackupError, Errors raised while creating or restoring backups., A backup could not be created or restored. (+12 more)

### Community 6 - "SelectionTree"
Cohesion: 0.07
Nodes (23): pytest, QTreeWidget, QTreeWidgetItem, _children(), Kind, QWidget, StrEnum, What a tree item stands for (stored in ``ROLE_KIND``). (+15 more)

### Community 7 - "build.py"
Cohesion: 0.07
Nodes (32): CI workflow, lint job (ruff format, ruff check, pyright), test job (pytest on Windows + Ubuntu matrix), build job (Windows exe / Linux tar.gz), Code signing (SignPath Foundation / OSSign), release job (draft GitHub release), Release workflow, SHA256SUMS.txt checksums (+24 more)

### Community 8 - "test_i18n.py"
Cohesion: 0.14
Nodes (16): run(), PySide6 user interface. - ``app``: start the application - ``main_window``:…, Language code for a locale name such as ``"de_DE"`` (default: the system…, system_language(), main(), Entry point: ``python -m obs_backup`` or the ``backup-restore-for-obs`` command., string, placeholders() (+8 more)

### Community 9 - "config.py"
Cohesion: 0.15
Nodes (23): ConfigParser, contextlib, itertools, full_selection(), Everything worth keeping, except browser data (large, and rarely restored)., _CaseKeepingParser, has_browser_data(), has_global_settings() (+15 more)

### Community 10 - "InstallPanel"
Cohesion: 0.09
Nodes (33): enum, psutil, QGroupBox, InstallPanel, Path, QWidget, Check whether OBS is running and show it, with the OBS version., Lists the OBS config folders found and checks regularly whether OBS is running. (+25 more)

### Community 11 - "layout.py"
Cohesion: 0.29
Nodes (7): ntpath, re, can_create(), creatable_name(), Layout of a backup file. A backup is a plain zip file:: manifest.json what the…, Whether this OS allows every name in ``rel`` (a ``/``-separated path). A backup…, ``name``, changed where needed so that this OS can create a file with it.

### Community 12 - "media.py"
Cohesion: 0.17
Nodes (16): find_media_files(), iter_strings(), load_scene_json(), looks_like_local_path(), Any, Path, Find and rewrite the local file paths that scene collections refer to. Sources…, Absolute paths of existing files referenced by a scene collection, as stored. (+8 more)

### Community 13 - "Backup Selection Checkbox Tree"
Cohesion: 0.16
Nodes (16): Backup Selection Checkbox Tree, Back up Tab, Browser Source & Dock Data (Cookies, Logins), Create Backup Button, General Settings (global.ini, user.ini, Plugin Manager), Include Media Files Used by Scenes Option, Language Menu (Localization), OBS Backup & Restore Main Window (Screenshot) (+8 more)

### Community 14 - "Backup & Restore for OBS"
Cohesion: 0.12
Nodes (15): AI disclosure, Backup file format, Backup & Restore for OBS, Contributing, Download, Features, License, Privacy (+7 more)

### Community 15 - "restore.py"
Cohesion: 0.12
Nodes (35): is_plain_name(), Whether ``name`` is one file or folder name on this OS, safe to join to a…, RestoreResult, _apply(), _check_names(), _config_target(), _crc32(), _empty() (+27 more)

### Community 16 - "create.py"
Cohesion: 0.11
Nodes (28): datetime, platform, shutil, collect_files(), _is_browser_cache_dir(), _is_browser_skip_file(), Path, Work out which files a backup should contain. (+20 more)

### Community 17 - "manifest.py"
Cohesion: 0.22
Nodes (18): InvalidBackupError, A file is not a valid backup, or is damaged or unsafe., _damaged(), _flag(), _is_int(), _list(), list_backups(), Manifest (+10 more)

### Community 18 - "_frozen"
Cohesion: 0.50
Nodes (4): frozendict, K, _frozen(), V

### Community 19 - "BackupTab"
Cohesion: 0.18
Nodes (8): BackupTab, Path, QWidget, Show the contents of the currently selected OBS config folder., FolderEdit, Path, QWidget, A folder path with a “Browse…” button. Emits ``changed`` when the user edits…

### Community 21 - "GNU General Public License v2"
Cohesion: 0.40
Nodes (6): GNU General Public License v3, GNU Lesser General Public License v3, PyInstaller Bootloader Exception, GNU General Public License v2, PyInstaller licensing terms, PyInstaller run-time hooks (Apache 2.0)

### Community 22 - "RELEASE_NOTES_TEMPLATE.md"
Cohesion: 0.50
Nodes (3): AI disclosure, Download, Licenses

### Community 23 - "test_create.py"
Cohesion: 0.16
Nodes (13): io, _FailsHalfway, Any, MonkeyPatch, Path, A file that gives some data, then fails (as a region OBS holds locked would)., test_backup_contents(), test_backup_without_browser_and_media() (+5 more)

### Community 26 - "members_for"
Cohesion: 0.50
Nodes (4): _is_selected(), members_for(), Whether a file at ``rel`` (relative to the config folder) belongs to ``sel``., Zip members under ``config/`` that ``sel`` covers.

## Knowledge Gaps
- **28 isolated node(s):** `backup-restore-for-obs`, `Download`, `AI disclosure`, `Licenses`, `graphify` (+23 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 212 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Selection` connect `Selection` to `tr`, `backup/__init__.py`, `SelectionTree`, `config.py`, `restore.py`, `create.py`, `test_create.py`, `members_for`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `tr()` connect `tr` to `RestoreTab`, `AppSettings`, `SelectionTree`, `InstallPanel`, `BackupTab`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Why does `AppSettings` connect `AppSettings` to `tr`, `RestoreTab`, `test_i18n.py`, `InstallPanel`, `BackupTab`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `Selection` (e.g. with `collect_files()` and `safety_selection()`) actually correct?**
  _`Selection` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `AppSettings` (e.g. with `BackupTab` and `InstallPanel`) actually correct?**
  _`AppSettings` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `MainWindow` (e.g. with `BackupTab` and `InstallPanel`) actually correct?**
  _`MainWindow` has 17 INFERRED edges - model-reasoned connections that need verification._
- **What connects `backup-restore-for-obs`, `Download`, `AI disclosure` to the rest of the system?**
  _28 weakly-connected nodes found - possible documentation gaps or missing edges._