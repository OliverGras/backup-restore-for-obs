# Graph Report - obs_backup  (2026-11-22)

## Corpus Check
- 51 files · ~34,439 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 732 nodes · 1803 edges · 33 communities (30 shown, 3 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 131 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `52fc4d5d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main_window.py
- TaskRunner
- RestoreTab
- test_main_window.py
- Selection
- restore_with_safety_backup
- test_i18n.py
- build.py
- SelectionTree
- config.py
- InstallPanel
- _Plan
- collect.py
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
- _FailsHalfway
- CLAUDE.md
- psutil BSD 3-Clause License
- _is_selected
- backup_tab.py
- backup/__init__.py
- tr
- i18n/__init__.py
- obs/__init__.py
- _Unreadable

## God Nodes (most connected - your core abstractions)
1. `Selection` - 62 edges
2. `tr()` - 39 edges
3. `MainWindow` - 37 edges
4. `AppSettings` - 34 edges
5. `InstallPanel` - 26 edges
6. `TaskRunner` - 26 edges
7. `write()` - 23 edges
8. `RestoreTab` - 22 edges
9. `craft_backup()` - 22 edges
10. `_Plan` - 20 edges

## Surprising Connections (you probably didn't know these)
- `test_everything_but_browser_data_is_ticked_by_default()` --uses--> `SelectionTree`  [INFERRED]
  tests/gui/test_selection_tree.py → src/obs_backup/gui/selection_tree.py
- `test_select_none_and_all()` --uses--> `SelectionTree`  [INFERRED]
  tests/gui/test_selection_tree.py → src/obs_backup/gui/selection_tree.py
- `test_list_backups()` --calls--> `Selection`  [INFERRED]
  tests/backup/test_manifest.py → src/obs_backup/backup/models.py
- `test_list_backups_skips_damaged_manifests()` --calls--> `Selection`  [INFERRED]
  tests/backup/test_manifest.py → src/obs_backup/backup/models.py
- `test_list_backups_skips_file_that_vanished()` --calls--> `Selection`  [INFERRED]
  tests/backup/test_manifest.py → src/obs_backup/backup/models.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Selectable OBS Backup Categories** — docs_screenshot_profiles, docs_screenshot_scene_collections, docs_screenshot_general_settings, docs_screenshot_plugin_settings, docs_screenshot_browser_source_dock_data [EXTRACTED 1.00]
- **Backup Creation Flow (Source, Selection, Destination, Action)** — docs_screenshot_obs_installation_panel, docs_screenshot_backup_selection_tree, docs_screenshot_include_media_files, docs_screenshot_save_to_destination, docs_screenshot_create_backup_button [INFERRED 0.85]

## Communities (33 total, 3 thin omitted)

### Community 0 - "main_window.py"
Cohesion: 0.19
Nodes (14): html, pyside6_qtcore, pyside6_qtgui, pyside6_qtwidgets, QWidget, show_about(), Start the application., Names and fixed values used across the user interface. (+6 more)

### Community 1 - "TaskRunner"
Cohesion: 0.09
Nodes (23): QObject, _CallWorker, Any, BaseException, Slot, Run ``fn()`` in the background, then ``on_done(result)`` if no newer call came., Runs one task in the thread it is moved to., Runs one task at a time and reports its progress in the GUI thread. (+15 more)

### Community 2 - "RestoreTab"
Cohesion: 0.13
Nodes (11): BaseException, Path, QWidget, List the backups in the backup folder; keep or set the selected one., Allow restoring only with a valid backup, OBS closed and no task running., RestoreTab, task(), FolderEdit (+3 more)

### Community 3 - "test_main_window.py"
Cohesion: 0.08
Nodes (38): QCloseEvent, QMainWindow, setter, MainWindow, Slot, Create menus and widgets in the current language (again after a language…, AppSettings, Path (+30 more)

### Community 4 - "Selection"
Cohesion: 0.05
Nodes (94): contextlib, io, json, os, OSError, What to back up or restore., Selection, struct (+86 more)

### Community 5 - "restore_with_safety_backup"
Cohesion: 0.14
Nodes (16): What to back up before restoring ``restoring``: everything a restore can…, safety_selection(), BackupError, IncompleteSafetyBackupError, BaseException, Exception, Path, Errors raised while creating or restoring backups. (+8 more)

### Community 6 - "test_i18n.py"
Cohesion: 0.06
Nodes (29): pytest, run(), PySide6 user interface. - ``app``: start the application - ``main_window``:…, Language code for a locale name such as ``"de_DE"`` (default: the system…, system_language(), main(), Entry point: ``python -m obs_backup`` or the ``backup-restore-for-obs`` command., string (+21 more)

### Community 7 - "build.py"
Cohesion: 0.06
Nodes (37): CI workflow, lint job (ruff format, ruff check, pyright), test job (pytest on Windows + Ubuntu matrix), build job (Windows exe / Linux tar.gz), Code signing (SignPath Foundation / OSSign), release job (draft GitHub release), Release workflow, SHA256SUMS.txt checksums (+29 more)

### Community 8 - "SelectionTree"
Cohesion: 0.15
Nodes (13): QTreeWidget, QTreeWidgetItem, _children(), Kind, QWidget, StrEnum, Checkable tree of the things a backup can hold., “Select all” and “Select none” buttons for a tree. (+5 more)

### Community 9 - "config.py"
Cohesion: 0.15
Nodes (23): ConfigParser, dataclasses, itertools, full_selection(), Everything worth keeping, except browser data (large, and rarely restored)., _CaseKeepingParser, has_browser_data(), has_global_settings() (+15 more)

### Community 10 - "InstallPanel"
Cohesion: 0.09
Nodes (33): enum, psutil, QGroupBox, InstallPanel, Path, QWidget, Check whether OBS is running and show it, with the OBS version., Lists the OBS config folders found and checks regularly whether OBS is running. (+25 more)

### Community 11 - "_Plan"
Cohesion: 0.13
Nodes (22): creatable_name(), ``name``, changed where needed so that this OS can create a file with it., _check_fits(), _config_target(), _crc32(), _has_contents(), _holds(), _Plan (+14 more)

### Community 12 - "collect.py"
Cohesion: 0.11
Nodes (28): browser_files(), collect_files(), _is_browser_cache_dir(), _is_browser_skip_file(), Path, Work out which files a backup should contain., All files under ``root`` (or ``root`` itself if it is a file), sorted., The browser data a backup holds: everything but caches and lock files. (+20 more)

### Community 13 - "Backup Selection Checkbox Tree"
Cohesion: 0.16
Nodes (16): Backup Selection Checkbox Tree, Back up Tab, Browser Source & Dock Data (Cookies, Logins), Create Backup Button, General Settings (global.ini, user.ini, Plugin Manager), Include Media Files Used by Scenes Option, Language Menu (Localization), OBS Backup & Restore Main Window (Screenshot) (+8 more)

### Community 14 - "Backup & Restore for OBS"
Cohesion: 0.12
Nodes (15): AI disclosure, Backup file format, Backup & Restore for OBS, Contributing, Download, Features, License, Privacy (+7 more)

### Community 15 - "restore.py"
Cohesion: 0.17
Nodes (20): errno, InvalidBackupError, A file is not a valid backup, or is damaged or unsafe., _apply(), _check_names(), _empty(), _move(), Progress (+12 more)

### Community 16 - "create.py"
Cohesion: 0.14
Nodes (25): BinaryIO, datetime, platform, _add_complete_file(), _add_media_file(), _chunks(), _compression(), create_backup() (+17 more)

### Community 17 - "manifest.py"
Cohesion: 0.08
Nodes (46): ntpath, re, skipif, can_create(), is_impossible_name(), is_plain_name(), Layout of a backup file. A backup is a plain zip file:: manifest.json what the…, Whether ``name`` is one file or folder name on this OS, safe to join to a… (+38 more)

### Community 18 - "_frozen"
Cohesion: 0.50
Nodes (4): frozendict, K, _frozen(), V

### Community 19 - "BackupTab"
Cohesion: 0.16
Nodes (9): BackupTab, Path, QWidget, Count the media in the background: checking paths can be slow (network drives)., Show the contents of the currently selected OBS config folder., LatestCall, Runs functions in one background thread and hands their results to the GUI…, Drop the result of the pending call. (+1 more)

### Community 21 - "GNU General Public License v2"
Cohesion: 0.40
Nodes (6): GNU General Public License v3, GNU Lesser General Public License v3, PyInstaller Bootloader Exception, GNU General Public License v2, PyInstaller licensing terms, PyInstaller run-time hooks (Apache 2.0)

### Community 22 - "RELEASE_NOTES_TEMPLATE.md"
Cohesion: 0.50
Nodes (3): AI disclosure, Download, Licenses

### Community 23 - "_FailsHalfway"
Cohesion: 0.29
Nodes (4): _FailsHalfway, Any, A file that gives some data, then fails (as a region OBS holds locked would)., open_()

### Community 26 - "_is_selected"
Cohesion: 0.50
Nodes (4): _is_selected(), members_for(), Whether a file at ``rel`` (relative to the config folder) belongs to ``sel``., Zip members under ``config/`` that ``sel`` covers.

### Community 27 - "backup_tab.py"
Cohesion: 0.22
Nodes (12): pathlib, “Back up” tab: choose what to save and create the backup., absolute_path(), documents_dir(), format_size(), open_folder(), preview_list(), Path (+4 more)

### Community 28 - "backup/__init__.py"
Cohesion: 0.22
Nodes (12): _manifest(), Backup files: what goes into them, creating them and restoring them. -…, list_backups(), Manifest, Path, Valid backups in ``folder``, newest first., read_manifest(), BackupResult (+4 more)

### Community 29 - "tr"
Cohesion: 0.24
Nodes (8): error_message(), BaseException, The text shown for an error that a backup or restore raised., current_language(), The text for ``key`` in the current language, with ``{placeholders}`` filled in., set_language(), tr(), test_tr_falls_back_and_formats()

### Community 30 - "i18n/__init__.py"
Cohesion: 0.18
Nodes (7): collections_abc, locale, Run long operations in background threads. - ``TaskRunner``: backup and…, German texts (Deutsch)., English texts. This is the reference language: every key must exist here.…, UI texts and the current language. Each language lives in its own module…, traceback

### Community 31 - "obs/__init__.py"
Cohesion: 0.33
Nodes (5): Knowledge about OBS Studio itself. - ``locator``: find OBS installations and…, Path, Reading profiles, scene collections and the OBS version., test_general_settings_found_by_any_of_their_parts(), test_reads_config()

### Community 32 - "_Unreadable"
Cohesion: 0.67
Nodes (3): Exception, A file to back up could not be read; the backup goes on without it. Kept apart…, _Unreadable

## Knowledge Gaps
- **28 isolated node(s):** `backup-restore-for-obs`, `Download`, `AI disclosure`, `Licenses`, `graphify` (+23 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 237 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Selection` connect `Selection` to `restore_with_safety_backup`, `SelectionTree`, `config.py`, `_Plan`, `collect.py`, `restore.py`, `create.py`, `manifest.py`, `_is_selected`, `backup/__init__.py`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Why does `tr()` connect `tr` to `main_window.py`, `RestoreTab`, `test_main_window.py`, `build.py`, `SelectionTree`, `InstallPanel`, `BackupTab`, `backup_tab.py`, `i18n/__init__.py`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Why does `AppSettings` connect `test_main_window.py` to `main_window.py`, `RestoreTab`, `test_i18n.py`, `InstallPanel`, `BackupTab`, `backup_tab.py`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Are the 50 inferred relationships involving `Selection` (e.g. with `collect_files()` and `safety_selection()`) actually correct?**
  _`Selection` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `MainWindow` (e.g. with `BackupTab` and `InstallPanel`) actually correct?**
  _`MainWindow` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `AppSettings` (e.g. with `BackupTab` and `InstallPanel`) actually correct?**
  _`AppSettings` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `backup-restore-for-obs`, `Download`, `AI disclosure` to the rest of the system?**
  _28 weakly-connected nodes found - possible documentation gaps or missing edges._