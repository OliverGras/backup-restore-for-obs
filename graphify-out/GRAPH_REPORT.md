# Graph Report - obs_backup  (2026-11-22)

## Corpus Check
- 51 files · ~35,749 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 760 nodes · 1884 edges · 48 communities (44 shown, 4 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 146 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7b3ccf4a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main_window.py
- .__init__
- RestoreTab
- test_main_window.py
- test_restore.py
- errors.py
- test_tasks.py
- build.py
- SelectionTree
- config.py
- InstallPanel
- restore.py
- media.py
- Backup Selection Checkbox Tree
- Backup & Restore for OBS
- Path
- create.py
- test_manifest.py
- _frozen
- TaskRunner
- backup-restore-for-obs
- GNU General Public License v2
- RELEASE_NOTES_TEMPLATE.md
- _FailsHalfway
- CLAUDE.md
- psutil BSD 3-Clause License
- Selection
- open_folder
- backup/__init__.py
- tr
- de.py
- obs/__init__.py
- _Unreadable
- test_i18n.py
- unreadable
- manifest.py
- create_backup
- collect.py
- pathlib
- support.py
- _plan_media
- write
- test_backup_from_an_older_version_removes_no_files
- FolderEdit
- safety_selection
- error_message
- _link
- LicensesDialog

## God Nodes (most connected - your core abstractions)
1. `Selection` - 69 edges
2. `tr()` - 40 edges
3. `MainWindow` - 37 edges
4. `AppSettings` - 34 edges
5. `write()` - 28 edges
6. `InstallPanel` - 26 edges
7. `TaskRunner` - 26 edges
8. `craft_backup()` - 24 edges
9. `RestoreTab` - 22 edges
10. `create_backup()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `test_language_change_replaces_the_menus()` --uses--> `MainWindow`  [INFERRED]
  tests/gui/test_main_window.py → src/obs_backup/gui/main_window.py
- `test_everything_but_browser_data_is_ticked_by_default()` --uses--> `SelectionTree`  [INFERRED]
  tests/gui/test_selection_tree.py → src/obs_backup/gui/selection_tree.py
- `test_select_none_and_all()` --uses--> `SelectionTree`  [INFERRED]
  tests/gui/test_selection_tree.py → src/obs_backup/gui/selection_tree.py
- `walk()` --indirect_call--> `unreadable()`  [INFERRED]
  src/obs_backup/backup/collect.py → tests/support.py
- `test_list_backups()` --calls--> `Selection`  [INFERRED]
  tests/backup/test_manifest.py → src/obs_backup/backup/models.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Selectable OBS Backup Categories** — docs_screenshot_profiles, docs_screenshot_scene_collections, docs_screenshot_general_settings, docs_screenshot_plugin_settings, docs_screenshot_browser_source_dock_data [EXTRACTED 1.00]
- **Backup Creation Flow (Source, Selection, Destination, Action)** — docs_screenshot_obs_installation_panel, docs_screenshot_backup_selection_tree, docs_screenshot_include_media_files, docs_screenshot_save_to_destination, docs_screenshot_create_backup_button [INFERRED 0.85]

## Communities (48 total, 4 thin omitted)

### Community 0 - "main_window.py"
Cohesion: 0.16
Nodes (19): locale, pyside6_qtcore, pyside6_qtgui, pyside6_qtwidgets, Start the application., “Back up” tab: choose what to save and create the backup., Names and fixed values used across the user interface., absolute_path() (+11 more)

### Community 1 - ".__init__"
Cohesion: 0.12
Nodes (10): QObject, _CallWorker, Any, BaseException, Slot, Run ``fn()`` in the background, then ``on_done(result)`` if no newer call came., Runs one task in the thread it is moved to., Start ``fn(progress)`` in the background. Afterwards ``on_done(result)`` runs,… (+2 more)

### Community 2 - "RestoreTab"
Cohesion: 0.20
Nodes (7): BaseException, Path, QWidget, List the backups in the backup folder; keep or set the selected one., Allow restoring only with a valid backup, OBS closed and no task running., RestoreTab, task()

### Community 3 - "test_main_window.py"
Cohesion: 0.10
Nodes (32): setter, AppSettings, Path, Typed access to the app's QSettings (registry on Windows, a .conf file on…, None (or a relative path) means the default folder., None (or a relative path) means the default folder., app(), fixture (+24 more)

### Community 4 - "test_restore.py"
Cohesion: 0.13
Nodes (32): _files(), parametrize, Path, Restoring backups, including media remapping and unsafe archives., A path that stays inside the config folder but leaves the selected profile., Chromium's databases must not meet newer journal or log files., On Windows, zipfile reads "a\\b/basic.ini" as "a/b/basic.ini": a file of "a"., zipfile cuts such a name short, which would restore "a" for "a\\0../../evil". (+24 more)

### Community 5 - "errors.py"
Cohesion: 0.15
Nodes (12): BackupError, IncompleteSafetyBackupError, BaseException, Exception, Path, Errors raised while creating or restoring backups. Each error names its message…, A backup could not be created or restored. A param that is an exception (the…, A restore failed; ``safety_backup`` holds the config folder as it was before. (+4 more)

### Community 6 - "test_tasks.py"
Cohesion: 0.09
Nodes (24): pytest, fixture, The selection tree turns ticked items into a backup.Selection., test_everything_but_browser_data_is_ticked_by_default(), test_select_none_and_all(), tree(), app(), _fail() (+16 more)

### Community 7 - "build.py"
Cohesion: 0.07
Nodes (33): CI workflow, lint job (ruff format, ruff check, pyright), test job (pytest on Windows + Ubuntu matrix), build job (Windows exe / Linux tar.gz), Code signing (SignPath Foundation / OSSign), release job (draft GitHub release), Release workflow, SHA256SUMS.txt checksums (+25 more)

### Community 8 - "SelectionTree"
Cohesion: 0.14
Nodes (13): QTreeWidget, QTreeWidgetItem, _children(), Kind, QWidget, StrEnum, Checkable tree of the things a backup can hold., “Select all” and “Select none” buttons for a tree. (+5 more)

### Community 9 - "config.py"
Cohesion: 0.14
Nodes (24): ConfigParser, contextlib, dataclasses, itertools, full_selection(), Everything worth keeping, except browser data (large, and rarely restored)., _CaseKeepingParser, has_browser_data() (+16 more)

### Community 10 - "InstallPanel"
Cohesion: 0.09
Nodes (35): enum, html, psutil, QGroupBox, InstallPanel, Path, QWidget, Top panel: which OBS config folder to use, and whether OBS is running. (+27 more)

### Community 11 - "restore.py"
Cohesion: 0.14
Nodes (21): _check_fits(), _check_names(), _config_target(), _holds(), _is_selected(), members_for(), _Plan, ZipFile (+13 more)

### Community 12 - "media.py"
Cohesion: 0.29
Nodes (11): dump_scene_json(), find_media_files(), iter_strings(), load_scene_json(), looks_like_local_path(), Any, Path, Find and rewrite the local file paths that scene collections refer to. Sources… (+3 more)

### Community 13 - "Backup Selection Checkbox Tree"
Cohesion: 0.16
Nodes (16): Backup Selection Checkbox Tree, Back up Tab, Browser Source & Dock Data (Cookies, Logins), Create Backup Button, General Settings (global.ini, user.ini, Plugin Manager), Include Media Files Used by Scenes Option, Language Menu (Localization), OBS Backup & Restore Main Window (Screenshot) (+8 more)

### Community 14 - "Backup & Restore for OBS"
Cohesion: 0.12
Nodes (15): AI disclosure, Backup file format, Backup & Restore for OBS, Contributing, Download, Features, License, Privacy (+7 more)

### Community 15 - "Path"
Cohesion: 0.26
Nodes (14): RestoreResult, _apply(), _empty(), _move(), Path, Progress, Move the unpacked file ``src`` to ``dst``, replacing the file there., Unpack everything ``plan`` covers, then move it into place. (+6 more)

### Community 16 - "create.py"
Cohesion: 0.18
Nodes (17): BinaryIO, datetime, errno, platform, _add_complete_file(), _add_media_file(), _chunks(), _compression() (+9 more)

### Community 17 - "test_manifest.py"
Cohesion: 0.15
Nodes (24): skipif, is_plain_name(), Whether ``name`` is one file or folder name on this OS, safe to join to a…, MonkeyPatch, parametrize, Path, Reading manifests and listing backups., A backup from Linux stays usable on Windows, without what Windows can't hold. (+16 more)

### Community 18 - "_frozen"
Cohesion: 0.50
Nodes (4): frozendict, K, _frozen(), V

### Community 19 - "TaskRunner"
Cohesion: 0.13
Nodes (11): BackupTab, Path, QWidget, Count the media in the background: checking paths can be slow (network drives)., Show the contents of the currently selected OBS config folder., LatestCall, Runs functions in one background thread and hands their results to the GUI…, Drop the result of the pending call. (+3 more)

### Community 21 - "GNU General Public License v2"
Cohesion: 0.40
Nodes (6): GNU General Public License v3, GNU Lesser General Public License v3, PyInstaller Bootloader Exception, GNU General Public License v2, PyInstaller licensing terms, PyInstaller run-time hooks (Apache 2.0)

### Community 22 - "RELEASE_NOTES_TEMPLATE.md"
Cohesion: 0.50
Nodes (3): AI disclosure, Download, Licenses

### Community 23 - "_FailsHalfway"
Cohesion: 0.29
Nodes (4): _FailsHalfway, Any, A file that gives some data, then fails (as a region OBS holds locked would)., open_()

### Community 26 - "Selection"
Cohesion: 0.16
Nodes (21): io, What to back up or restore., Selection, MonkeyPatch, Path, A full disk is not a file OBS holds open: the backup fails instead of skipping., Another copy of the app may finish a backup of the same name first., test_backup_being_written_is_left_alone() (+13 more)

### Community 27 - "open_folder"
Cohesion: 0.22
Nodes (6): format_size(), open_folder(), Path, Show a folder in the system file manager., preview_list(), The first ``limit`` items, one per line, with "…" if there are more.

### Community 28 - "backup/__init__.py"
Cohesion: 0.26
Nodes (11): InvalidBackupError, A file is not a valid backup, or is damaged or unsafe., Backup files: what goes into them, creating them and restoring them. -…, list_backups(), Manifest, ProfileEntry, Path, Valid backups in ``folder``, newest first. (+3 more)

### Community 29 - "tr"
Cohesion: 0.15
Nodes (13): QCloseEvent, QMainWindow, QWidget, show_about(), MainWindow, BaseException, Slot, Create menus and widgets in the current language (again after a language… (+5 more)

### Community 31 - "obs/__init__.py"
Cohesion: 0.33
Nodes (5): Knowledge about OBS Studio itself. - ``locator``: find OBS installations and…, Path, Reading profiles, scene collections and the OBS version., test_general_settings_found_by_any_of_their_parts(), test_reads_config()

### Community 32 - "_Unreadable"
Cohesion: 0.67
Nodes (3): Exception, A file to back up could not be read; the backup goes on without it. Kept apart…, _Unreadable

### Community 33 - "test_i18n.py"
Cohesion: 0.11
Nodes (20): run(), PySide6 user interface. - ``app``: start the application - ``main_window``:…, Language code for a locale name such as ``"de_DE"`` (default: the system…, system_language(), main(), Entry point: ``python -m obs_backup`` or the ``backup-restore-for-obs`` command., string, error_codes() (+12 more)

### Community 34 - "unreadable"
Cohesion: 0.13
Nodes (16): OSError, on_windows(), fixture, MonkeyPatch, Apply Windows' file name rules, whatever OS the tests run on., ``os.replace`` fails for files unpacked to the restore's temporary folder., _replace_failing_from_staging(), test_browser_data_backed_up_partly_is_restored_over_current() (+8 more)

### Community 35 - "manifest.py"
Cohesion: 0.24
Nodes (17): can_create(), is_impossible_name(), Whether no OS has a file or folder called ``name`` (``..``, ``a/b``)., Whether this OS allows every name in ``rel`` (a ``/``-separated path). A backup…, _damaged(), _flag(), _is_int(), _list() (+9 more)

### Community 36 - "create_backup"
Cohesion: 0.17
Nodes (15): collections_abc, Media files the given scene collections use and that exist on this machine., scan_media(), create_backup(), _manifest(), _part(), _publish(), Path (+7 more)

### Community 37 - "collect.py"
Cohesion: 0.22
Nodes (13): os, browser_files(), _children(), collect_files(), walk(), _is_browser_cache_dir(), _is_browser_skip_file(), Path (+5 more)

### Community 38 - "pathlib"
Cohesion: 0.14
Nodes (12): ntpath, pathlib, re, Layout of a backup file. A backup is a plain zip file:: manifest.json what the…, file_name(), File name of a path that may come from another OS., sys, Path (+4 more)

### Community 39 - "support.py"
Cohesion: 0.21
Nodes (10): json, struct, media(), obs(), fixture, Path, Test data: a fake OBS config folder with profiles, scene collections and media., An OBS config folder like a real one, small enough for tests. (+2 more)

### Community 40 - "_plan_media"
Cohesion: 0.24
Nodes (10): creatable_name(), ``name``, changed where needed so that this OS can create a file with it., _crc32(), _has_contents(), _plan_media(), ZipInfo, Whether the file at ``path`` holds exactly the zip member ``info``., Where to put the media file ``info`` in ``media_dir``. A file that already… (+2 more)

### Community 41 - "write"
Cohesion: 0.27
Nodes (10): _restored_paths(), _scene_using(), test_existing_media_reused_only_with_the_same_contents(), test_failed_safety_backup_is_not_named(), test_file_in_the_way_of_a_folder_stops_before_any_change(), test_file_where_an_emptied_profile_folder_goes_stops_before_any_change(), test_folder_in_the_way_stops_before_any_change(), test_media_with_the_same_name_are_kept_apart() (+2 more)

### Community 42 - "test_backup_from_an_older_version_removes_no_files"
Cohesion: 0.22
Nodes (9): Older backups don't record which files they lack, so none count as complete., test_backup_from_an_older_version_removes_no_files(), test_damaged_member_leaves_config_untouched(), test_failed_restore_names_the_safety_backup(), corrupt_member(), Path, Flip a byte in the stored data of one member, as a damaged download would., Replace one member of a zip (rewrites the whole file). (+1 more)

### Community 43 - "FolderEdit"
Cohesion: 0.46
Nodes (4): FolderEdit, Path, QWidget, A folder path with a “Browse…” button. Emits ``changed`` when the user edits…

### Community 44 - "safety_selection"
Cohesion: 0.33
Nodes (6): What to back up before restoring ``restoring``: everything a restore can…, safety_selection(), default_backup_name(), new_backup_path(), A path in ``folder`` for a new backup that no other backup uses yet. Backups…, back_up_current_state()

### Community 45 - "error_message"
Cohesion: 0.33
Nodes (6): describe(), The message of an error that is not one of ours (an OSError, a zip error)., error_message(), BaseException, The message of ``error`` for the user: in their language if the app raised it., test_errors_are_worded_in_the_chosen_language()

### Community 46 - "_link"
Cohesion: 0.47
Nodes (6): _is_link(), _link(), A symlink, or on Windows without the rights for one, a junction., test_linked_folder_inside_a_profile_survives_the_restore(), test_restore_into_linked_profile_folder(), test_restore_into_linked_scenes_folder()

### Community 47 - "LicensesDialog"
Cohesion: 0.40
Nodes (3): QDialog, QUrl, LicensesDialog

## Knowledge Gaps
- **28 isolated node(s):** `backup-restore-for-obs`, `Download`, `AI disclosure`, `Licenses`, `graphify` (+23 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 250 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Selection` connect `Selection` to `unreadable`, `create_backup`, `collect.py`, `test_restore.py`, `_plan_media`, `config.py`, `SelectionTree`, `restore.py`, `safety_selection`, `test_backup_from_an_older_version_removes_no_files`, `write`, `Path`, `create.py`, `test_manifest.py`, `_link`, `backup/__init__.py`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Why does `tr()` connect `tr` to `main_window.py`, `RestoreTab`, `test_main_window.py`, `build.py`, `SelectionTree`, `InstallPanel`, `FolderEdit`, `error_message`, `TaskRunner`, `open_folder`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Why does `AppSettings` connect `test_main_window.py` to `main_window.py`, `test_i18n.py`, `RestoreTab`, `SelectionTree`, `InstallPanel`, `TaskRunner`, `tr`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 57 inferred relationships involving `Selection` (e.g. with `collect_files()` and `safety_selection()`) actually correct?**
  _`Selection` has 57 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `MainWindow` (e.g. with `BackupTab` and `InstallPanel`) actually correct?**
  _`MainWindow` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `AppSettings` (e.g. with `BackupTab` and `InstallPanel`) actually correct?**
  _`AppSettings` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `backup-restore-for-obs`, `Download`, `AI disclosure` to the rest of the system?**
  _28 weakly-connected nodes found - possible documentation gaps or missing edges._