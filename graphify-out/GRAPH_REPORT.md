# Graph Report - obs_backup  (2026-11-22)

## Corpus Check
- 51 files · ~36,747 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 788 nodes · 1958 edges · 38 communities (35 shown, 3 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 154 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `bc6cfeed`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main_window.py
- TaskRunner
- AppSettings
- test_main_window.py
- test_restore.py
- backup/__init__.py
- SelectionTree
- build.py
- Selection
- config.py
- InstallPanel
- restore.py
- unreadable
- Backup Selection Checkbox Tree
- Backup & Restore for OBS
- tr
- create.py
- craft_backup
- collect.py
- support.py
- backup-restore-for-obs
- GNU General Public License v2
- RELEASE_NOTES_TEMPLATE.md
- _FailsHalfway
- CLAUDE.md
- psutil BSD 3-Clause License
- restore_with_safety_backup
- licenses_dialog.py
- helpers.py
- i18n/__init__.py
- describe
- walk
- test_config.py
- test_i18n.py
- error_message
- manifest.py
- _Unreadable
- pathlib

## God Nodes (most connected - your core abstractions)
1. `Selection` - 78 edges
2. `tr()` - 40 edges
3. `MainWindow` - 37 edges
4. `AppSettings` - 34 edges
5. `write()` - 32 edges
6. `InstallPanel` - 26 edges
7. `TaskRunner` - 26 edges
8. `craft_backup()` - 25 edges
9. `RestoreTab` - 22 edges
10. `create_backup()` - 21 edges

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

## Communities (38 total, 3 thin omitted)

### Community 0 - "main_window.py"
Cohesion: 0.16
Nodes (18): html, pyside6_qtcore, pyside6_qtwidgets, QWidget, show_about(), Start the application., “Back up” tab: choose what to save and create the backup., Names and fixed values used across the user interface. (+10 more)

### Community 1 - "TaskRunner"
Cohesion: 0.06
Nodes (33): QObject, BackupTab, Path, QWidget, Count the media in the background: checking paths can be slow (network drives)., Show the contents of the currently selected OBS config folder., _CallWorker, LatestCall (+25 more)

### Community 2 - "AppSettings"
Cohesion: 0.09
Nodes (17): setter, BaseException, Path, QWidget, List the backups in the backup folder; keep or set the selected one., Allow restoring only with a valid backup, OBS closed and no task running., RestoreTab, task() (+9 more)

### Community 3 - "test_main_window.py"
Cohesion: 0.12
Nodes (30): QMainWindow, MainWindow, BaseException, Slot, app(), fixture, MonkeyPatch, parametrize (+22 more)

### Community 4 - "test_restore.py"
Cohesion: 0.11
Nodes (40): Path, skipif, Restoring backups, including media remapping and unsafe archives., Chromium's databases must not meet newer journal or log files., zipfile cuts such a name short, which would restore "a" for "a\\0../../evil"., Older backups don't record which files they lack, so none count as complete., On Linux, "C:/m/logo.png" is a relative path: it must not count as present., _restored_paths() (+32 more)

### Community 5 - "backup/__init__.py"
Cohesion: 0.12
Nodes (24): dataclasses, Media files the given scene collections use and that exist on this machine., scan_media(), BackupError, IncompleteSafetyBackupError, InvalidBackupError, Exception, Errors raised while creating or restoring backups. Each error names its message… (+16 more)

### Community 6 - "SelectionTree"
Cohesion: 0.07
Nodes (23): pytest, QTreeWidget, QTreeWidgetItem, _children(), Kind, QWidget, StrEnum, What a tree item stands for (stored in ``ROLE_KIND``). (+15 more)

### Community 7 - "build.py"
Cohesion: 0.07
Nodes (32): CI workflow, lint job (ruff format, ruff check, pyright), test job (pytest on Windows + Ubuntu matrix), build job (Windows exe / Linux tar.gz), Code signing (SignPath Foundation / OSSign), release job (draft GitHub release), Release workflow, SHA256SUMS.txt checksums (+24 more)

### Community 8 - "Selection"
Cohesion: 0.12
Nodes (30): io, socket, What to back up or restore., Selection, MonkeyPatch, Path, A full disk is not a file OBS holds open: the backup fails instead of skipping., Another copy of the app may finish a backup of the same name first. (+22 more)

### Community 9 - "config.py"
Cohesion: 0.15
Nodes (23): ConfigParser, contextlib, itertools, full_selection(), Everything worth keeping, except browser data (large, and rarely restored)., _CaseKeepingParser, has_browser_data(), has_global_settings() (+15 more)

### Community 10 - "InstallPanel"
Cohesion: 0.09
Nodes (33): enum, psutil, QGroupBox, InstallPanel, Path, QWidget, Check whether OBS is running and show it, with the OBS version., Lists the OBS config folders found and checks regularly whether OBS is running. (+25 more)

### Community 11 - "restore.py"
Cohesion: 0.11
Nodes (37): creatable_name(), ``name``, changed where needed so that this OS can create a file with it., _apply(), _check_fits(), _config_target(), _crc32(), _empty(), _has_contents() (+29 more)

### Community 12 - "unreadable"
Cohesion: 0.13
Nodes (16): OSError, on_windows(), fixture, MonkeyPatch, Apply Windows' file name rules, whatever OS the tests run on., ``os.replace`` fails for files unpacked to the restore's temporary folder., _replace_failing_from_staging(), test_browser_data_backed_up_partly_is_restored_over_current() (+8 more)

### Community 13 - "Backup Selection Checkbox Tree"
Cohesion: 0.16
Nodes (16): Backup Selection Checkbox Tree, Back up Tab, Browser Source & Dock Data (Cookies, Logins), Create Backup Button, General Settings (global.ini, user.ini, Plugin Manager), Include Media Files Used by Scenes Option, Language Menu (Localization), OBS Backup & Restore Main Window (Screenshot) (+8 more)

### Community 14 - "Backup & Restore for OBS"
Cohesion: 0.12
Nodes (15): AI disclosure, Backup file format, Backup & Restore for OBS, Contributing, Download, Features, License, Privacy (+7 more)

### Community 15 - "tr"
Cohesion: 0.19
Nodes (8): QCloseEvent, format_size(), Create menus and widgets in the current language (again after a language…, current_language(), The text for ``key`` in the current language, with ``{placeholders}`` filled in., set_language(), tr(), test_tr_falls_back_and_formats()

### Community 16 - "create.py"
Cohesion: 0.12
Nodes (30): BinaryIO, datetime, errno, platform, shutil, _add_complete_file(), _add_media_file(), _chunks() (+22 more)

### Community 17 - "craft_backup"
Cohesion: 0.18
Nodes (16): _files(), parametrize, A path that stays inside the config folder but leaves the selected profile., On Windows, zipfile reads "a\\b/basic.ini" as "a/b/basic.ini": a file of "a"., test_crafted_profile_name_cannot_delete_config(), test_files_of_a_linux_profile_with_backslash_stay_out_of_other_profiles(), test_incomplete_safety_backup_stops_the_restore(), test_media_name_windows_refuses_is_changed() (+8 more)

### Community 18 - "collect.py"
Cohesion: 0.22
Nodes (13): browser_files(), _children(), collect_files(), walk(), _is_browser_cache_dir(), _is_browser_skip_file(), Path, Work out which files a backup should contain. (+5 more)

### Community 19 - "support.py"
Cohesion: 0.18
Nodes (14): struct, Such a link (Chromium leaves some after a crash) holds nothing to lose., test_link_where_the_backup_has_a_file_stops_before_any_change(), test_link_whose_target_is_gone_does_not_stop_the_restore(), test_linked_folder_inside_a_profile_survives_the_restore(), test_restore_into_linked_profile_folder(), test_restore_into_linked_scenes_folder(), is_link() (+6 more)

### Community 21 - "GNU General Public License v2"
Cohesion: 0.40
Nodes (6): GNU General Public License v3, GNU Lesser General Public License v3, PyInstaller Bootloader Exception, GNU General Public License v2, PyInstaller licensing terms, PyInstaller run-time hooks (Apache 2.0)

### Community 22 - "RELEASE_NOTES_TEMPLATE.md"
Cohesion: 0.50
Nodes (3): AI disclosure, Download, Licenses

### Community 23 - "_FailsHalfway"
Cohesion: 0.29
Nodes (4): _FailsHalfway, Any, A file that gives some data, then fails (as a region OBS holds locked would)., open_()

### Community 26 - "restore_with_safety_backup"
Cohesion: 0.22
Nodes (13): What to back up before restoring ``restoring``: everything a restore can…, safety_selection(), RestoreResult, _check_names(), _is_selected(), Progress, Whether a file at ``rel`` (relative to the config folder) belongs to ``sel``., Restore the selected parts of a backup into ``config_dir``. OBS must not be… (+5 more)

### Community 27 - "licenses_dialog.py"
Cohesion: 0.20
Nodes (6): pyside6_qtgui, QDialog, QUrl, LicensesDialog, QWidget, Dialog listing the app's own license and the bundled third-party licenses.

### Community 28 - "helpers.py"
Cohesion: 0.27
Nodes (7): absolute_path(), documents_dir(), open_folder(), Path, Small helpers for the user interface., ``text`` as a path, or None if it is empty or relative. A relative path would…, Show a folder in the system file manager.

### Community 29 - "i18n/__init__.py"
Cohesion: 0.22
Nodes (6): locale, German texts (Deutsch)., English texts. This is the reference language: every key must exist here.…, preview_list(), UI texts and the current language. Each language lives in its own module…, The first ``limit`` items, one per line, with "…" if there are more.

### Community 30 - "describe"
Cohesion: 0.33
Nodes (4): describe(), BaseException, Path, The message of an error that is not one of ours (an OSError, a zip error).

### Community 31 - "walk"
Cohesion: 0.40
Nodes (6): DirEntry, _is_file(), _is_real_folder(), A folder that is not a link to one (symlink or junction)., A regular file, or a link to one., walk()

### Community 32 - "test_config.py"
Cohesion: 0.50
Nodes (4): Path, Reading profiles, scene collections and the OBS version., test_general_settings_found_by_any_of_their_parts(), test_reads_config()

### Community 33 - "test_i18n.py"
Cohesion: 0.09
Nodes (24): frozendict, K, run(), PySide6 user interface. - ``app``: start the application - ``main_window``:…, _frozen(), Language code for a locale name such as ``"de_DE"`` (default: the system…, system_language(), main() (+16 more)

### Community 34 - "error_message"
Cohesion: 0.50
Nodes (4): error_message(), BaseException, The message of ``error`` for the user: in their language if the app raised it., test_errors_are_worded_in_the_chosen_language()

### Community 35 - "manifest.py"
Cohesion: 0.07
Nodes (49): json, can_create(), is_impossible_name(), is_plain_name(), Whether ``name`` is one file or folder name on this OS, safe to join to a…, Whether no OS has a file or folder called ``name`` (``..``, ``a/b``)., Whether this OS allows every name in ``rel`` (a ``/``-separated path). A backup…, _damaged() (+41 more)

### Community 36 - "_Unreadable"
Cohesion: 0.67
Nodes (3): Exception, A file to back up could not be read; the backup goes on without it. Kept apart…, _Unreadable

### Community 37 - "pathlib"
Cohesion: 0.10
Nodes (26): collections_abc, ntpath, os, pathlib, re, Layout of a backup file. A backup is a plain zip file:: manifest.json what the…, file_name(), find_media_files() (+18 more)

## Knowledge Gaps
- **28 isolated node(s):** `backup-restore-for-obs`, `Download`, `AI disclosure`, `Licenses`, `graphify` (+23 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 261 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Selection` connect `Selection` to `main_window.py`, `manifest.py`, `test_restore.py`, `backup/__init__.py`, `SelectionTree`, `config.py`, `restore.py`, `unreadable`, `create.py`, `craft_backup`, `collect.py`, `support.py`, `restore_with_safety_backup`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Why does `tr()` connect `tr` to `main_window.py`, `TaskRunner`, `error_message`, `test_main_window.py`, `AppSettings`, `SelectionTree`, `InstallPanel`, `licenses_dialog.py`, `helpers.py`, `i18n/__init__.py`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `AppSettings` connect `AppSettings` to `main_window.py`, `test_i18n.py`, `TaskRunner`, `test_main_window.py`, `InstallPanel`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 66 inferred relationships involving `Selection` (e.g. with `collect_files()` and `safety_selection()`) actually correct?**
  _`Selection` has 66 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `MainWindow` (e.g. with `BackupTab` and `InstallPanel`) actually correct?**
  _`MainWindow` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `AppSettings` (e.g. with `BackupTab` and `InstallPanel`) actually correct?**
  _`AppSettings` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `backup-restore-for-obs`, `Download`, `AI disclosure` to the rest of the system?**
  _28 weakly-connected nodes found - possible documentation gaps or missing edges._