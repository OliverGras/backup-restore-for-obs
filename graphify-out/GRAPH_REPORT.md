# Graph Report - obs_backup  (2026-11-22)

## Corpus Check
- 51 files · ~36,089 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 769 nodes · 1913 edges · 27 communities (24 shown, 3 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 149 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `aa7505f6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- tr
- TaskRunner
- RestoreTab
- test_main_window.py
- Selection
- backup/__init__.py
- SelectionTree
- build job (Windows exe / Linux tar.gz)
- config.py
- InstallPanel
- restore.py
- Backup Selection Checkbox Tree
- Backup & Restore for OBS
- create.py
- test_manifest.py
- _frozen
- BackupTab
- backup-restore-for-obs
- GNU General Public License v2
- RELEASE_NOTES_TEMPLATE.md
- _FailsHalfway
- CLAUDE.md
- psutil BSD 3-Clause License
- InvalidBackupError
- test_i18n.py
- manifest.py
- collect.py

## God Nodes (most connected - your core abstractions)
1. `Selection` - 72 edges
2. `tr()` - 40 edges
3. `MainWindow` - 37 edges
4. `AppSettings` - 34 edges
5. `write()` - 30 edges
6. `InstallPanel` - 26 edges
7. `TaskRunner` - 26 edges
8. `craft_backup()` - 25 edges
9. `RestoreTab` - 22 edges
10. `create_backup()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `walk()` --indirect_call--> `unreadable()`  [INFERRED]
  src/obs_backup/backup/collect.py → tests/support.py
- `test_list_backups()` --calls--> `Selection`  [INFERRED]
  tests/backup/test_manifest.py → src/obs_backup/backup/models.py
- `test_list_backups_finds_upper_case_extension()` --calls--> `Selection`  [INFERRED]
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

## Communities (27 total, 3 thin omitted)

### Community 0 - "tr"
Cohesion: 0.05
Nodes (58): collections_abc, html, locale, pathlib, pyside6_qtcore, pyside6_qtgui, pyside6_qtwidgets, QDialog (+50 more)

### Community 1 - "TaskRunner"
Cohesion: 0.08
Nodes (27): QObject, _CallWorker, LatestCall, Any, BaseException, Slot, Runs functions in one background thread and hands their results to the GUI…, Run ``fn()`` in the background, then ``on_done(result)`` if no newer call came. (+19 more)

### Community 2 - "RestoreTab"
Cohesion: 0.20
Nodes (6): BaseException, Path, QWidget, List the backups in the backup folder; keep or set the selected one., Allow restoring only with a valid backup, OBS closed and no task running., RestoreTab

### Community 3 - "test_main_window.py"
Cohesion: 0.07
Nodes (39): QCloseEvent, QMainWindow, setter, MainWindow, Slot, Create menus and widgets in the current language (again after a language…, task(), AppSettings (+31 more)

### Community 4 - "Selection"
Cohesion: 0.05
Nodes (101): contextlib, io, OSError, What to back up or restore., Selection, struct, MonkeyPatch, Path (+93 more)

### Community 5 - "backup/__init__.py"
Cohesion: 0.13
Nodes (24): What to back up before restoring ``restoring``: everything a restore can…, safety_selection(), BackupError, IncompleteSafetyBackupError, Exception, Errors raised while creating or restoring backups. Each error names its message…, A backup could not be created or restored. A param that is an exception (the…, A restore failed; ``safety_backup`` holds the config folder as it was before. (+16 more)

### Community 6 - "SelectionTree"
Cohesion: 0.07
Nodes (23): pytest, QTreeWidget, QTreeWidgetItem, _children(), Kind, QWidget, StrEnum, What a tree item stands for (stored in ``ROLE_KIND``). (+15 more)

### Community 7 - "build job (Windows exe / Linux tar.gz)"
Cohesion: 0.17
Nodes (13): CI workflow, lint job (ruff format, ruff check, pyright), test job (pytest on Windows + Ubuntu matrix), build job (Windows exe / Linux tar.gz), Code signing (SignPath Foundation / OSSign), release job (draft GitHub release), Release workflow, SHA256SUMS.txt checksums (+5 more)

### Community 9 - "config.py"
Cohesion: 0.16
Nodes (22): ConfigParser, itertools, full_selection(), Everything worth keeping, except browser data (large, and rarely restored)., _CaseKeepingParser, has_browser_data(), has_global_settings(), has_plugin_config() (+14 more)

### Community 10 - "InstallPanel"
Cohesion: 0.09
Nodes (33): enum, psutil, QGroupBox, InstallPanel, Path, QWidget, Check whether OBS is running and show it, with the OBS version., Lists the OBS config folders found and checks regularly whether OBS is running. (+25 more)

### Community 11 - "restore.py"
Cohesion: 0.10
Nodes (35): dataclasses, creatable_name(), ``name``, changed where needed so that this OS can create a file with it., _check_fits(), _crc32(), _empty(), _has_contents(), _holds() (+27 more)

### Community 13 - "Backup Selection Checkbox Tree"
Cohesion: 0.16
Nodes (16): Backup Selection Checkbox Tree, Back up Tab, Browser Source & Dock Data (Cookies, Logins), Create Backup Button, General Settings (global.ini, user.ini, Plugin Manager), Include Media Files Used by Scenes Option, Language Menu (Localization), OBS Backup & Restore Main Window (Screenshot) (+8 more)

### Community 14 - "Backup & Restore for OBS"
Cohesion: 0.12
Nodes (15): AI disclosure, Backup file format, Backup & Restore for OBS, Contributing, Download, Features, License, Privacy (+7 more)

### Community 16 - "create.py"
Cohesion: 0.11
Nodes (33): BinaryIO, datetime, errno, platform, shutil, _add_complete_file(), _add_media_file(), _chunks() (+25 more)

### Community 17 - "test_manifest.py"
Cohesion: 0.14
Nodes (24): MonkeyPatch, parametrize, Path, skipif, Reading manifests and listing backups., A backup from Linux stays usable on Windows, without what Windows can't hold., test_backslash_separates_names_only_on_windows(), test_creatable_name() (+16 more)

### Community 18 - "_frozen"
Cohesion: 0.50
Nodes (4): frozendict, K, _frozen(), V

### Community 19 - "BackupTab"
Cohesion: 0.16
Nodes (10): BackupTab, Path, QWidget, Count the media in the background: checking paths can be slow (network drives)., Show the contents of the currently selected OBS config folder., FolderEdit, Path, QWidget (+2 more)

### Community 21 - "GNU General Public License v2"
Cohesion: 0.40
Nodes (6): GNU General Public License v3, GNU Lesser General Public License v3, PyInstaller Bootloader Exception, GNU General Public License v2, PyInstaller licensing terms, PyInstaller run-time hooks (Apache 2.0)

### Community 22 - "RELEASE_NOTES_TEMPLATE.md"
Cohesion: 0.50
Nodes (3): AI disclosure, Download, Licenses

### Community 23 - "_FailsHalfway"
Cohesion: 0.29
Nodes (4): _FailsHalfway, Any, A file that gives some data, then fails (as a region OBS holds locked would)., open_()

### Community 28 - "InvalidBackupError"
Cohesion: 0.24
Nodes (11): InvalidBackupError, A file is not a valid backup, or is damaged or unsafe., list_backups(), Manifest, Path, Valid backups in ``folder``, newest first., read_manifest(), _config_target() (+3 more)

### Community 33 - "test_i18n.py"
Cohesion: 0.06
Nodes (40): app_version(), copy_python_license(), main(), Path, Build the standalone app with PyInstaller. uv run python packaging/build.py…, Version resource (file properties → Details) for the Windows .exe. The numeric…, The license of the Python being bundled; it lists that build's own libraries.…, write_windows_version_info() (+32 more)

### Community 35 - "manifest.py"
Cohesion: 0.15
Nodes (25): ntpath, can_create(), is_impossible_name(), is_plain_name(), Layout of a backup file. A backup is a plain zip file:: manifest.json what the…, Whether ``name`` is one file or folder name on this OS, safe to join to a…, Whether no OS has a file or folder called ``name`` (``..``, ``a/b``)., Whether this OS allows every name in ``rel`` (a ``/``-separated path). A backup… (+17 more)

### Community 37 - "collect.py"
Cohesion: 0.07
Nodes (41): json, os, browser_files(), _children(), collect_files(), walk(), _is_browser_cache_dir(), _is_browser_skip_file() (+33 more)

## Knowledge Gaps
- **28 isolated node(s):** `backup-restore-for-obs`, `Download`, `AI disclosure`, `Licenses`, `graphify` (+23 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 253 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Selection` connect `Selection` to `tr`, `manifest.py`, `backup/__init__.py`, `collect.py`, `SelectionTree`, `config.py`, `restore.py`, `create.py`, `test_manifest.py`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Why does `tr()` connect `tr` to `RestoreTab`, `test_main_window.py`, `SelectionTree`, `InstallPanel`, `BackupTab`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `AppSettings` connect `test_main_window.py` to `tr`, `test_i18n.py`, `RestoreTab`, `InstallPanel`, `BackupTab`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 60 inferred relationships involving `Selection` (e.g. with `collect_files()` and `safety_selection()`) actually correct?**
  _`Selection` has 60 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `MainWindow` (e.g. with `BackupTab` and `InstallPanel`) actually correct?**
  _`MainWindow` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `AppSettings` (e.g. with `BackupTab` and `InstallPanel`) actually correct?**
  _`AppSettings` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `backup-restore-for-obs`, `Download`, `AI disclosure` to the rest of the system?**
  _28 weakly-connected nodes found - possible documentation gaps or missing edges._