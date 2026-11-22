# Graph Report - obs_backup  (2026-11-22)

## Corpus Check
- 51 files · ~37,843 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 804 nodes · 1993 edges · 45 communities (42 shown, 3 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 157 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `11ee93b8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main_window.py
- LatestCall
- RestoreTab
- test_main_window.py
- test_restore.py
- InvalidBackupError
- SelectionTree
- build job (Windows exe / Linux tar.gz)
- Selection
- config.py
- locator.py
- restore.py
- MonkeyPatch
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
- _Plan
- LicensesDialog
- FolderEdit
- i18n/__init__.py
- BackupError
- walk
- manifest.py
- test_i18n.py
- error_message
- test_manifest.py
- TaskRunner
- os
- InstallPanel
- create_backup
- media.py
- backup/__init__.py
- _plan_media
- layout.py
- _frozen

## God Nodes (most connected - your core abstractions)
1. `Selection` - 80 edges
2. `tr()` - 40 edges
3. `MainWindow` - 37 edges
4. `write()` - 35 edges
5. `AppSettings` - 34 edges
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

## Communities (45 total, 3 thin omitted)

### Community 0 - "main_window.py"
Cohesion: 0.16
Nodes (18): html, pathlib, pyside6_qtcore, pyside6_qtgui, pyside6_qtwidgets, Start the application., “Back up” tab: choose what to save and create the backup., Names and fixed values used across the user interface. (+10 more)

### Community 1 - "LatestCall"
Cohesion: 0.08
Nodes (25): QObject, _CallWorker, LatestCall, Any, BaseException, Slot, Runs functions in one background thread and hands their results to the GUI…, Run ``fn()`` in the background, then ``on_done(result)`` if no newer call came. (+17 more)

### Community 2 - "RestoreTab"
Cohesion: 0.20
Nodes (7): BaseException, Path, QWidget, List the backups in the backup folder; keep or set the selected one., Allow restoring only with a valid backup, OBS closed and no task running., RestoreTab, task()

### Community 3 - "test_main_window.py"
Cohesion: 0.08
Nodes (39): QCloseEvent, QMainWindow, setter, documents_dir(), MainWindow, Slot, Create menus and widgets in the current language (again after a language…, AppSettings (+31 more)

### Community 4 - "test_restore.py"
Cohesion: 0.14
Nodes (33): Path, Restoring backups, including media remapping and unsafe archives., Chromium's databases must not meet newer journal or log files., Older backups don't record which files they lack, so none count as complete., _restored_paths(), _scene_using(), test_backup_from_an_older_version_removes_no_files(), test_browser_data_replaces_files_written_since() (+25 more)

### Community 5 - "InvalidBackupError"
Cohesion: 0.24
Nodes (11): InvalidBackupError, A file is not a valid backup, or is damaged or unsafe., list_backups(), Manifest, Path, Valid backups in ``folder``, newest first., read_manifest(), _config_target() (+3 more)

### Community 6 - "SelectionTree"
Cohesion: 0.06
Nodes (29): pytest, QTreeWidget, QTreeWidgetItem, _children(), Kind, QWidget, StrEnum, What a tree item stands for (stored in ``ROLE_KIND``). (+21 more)

### Community 7 - "build job (Windows exe / Linux tar.gz)"
Cohesion: 0.17
Nodes (13): CI workflow, lint job (ruff format, ruff check, pyright), test job (pytest on Windows + Ubuntu matrix), build job (Windows exe / Linux tar.gz), Code signing (SignPath Foundation / OSSign), release job (draft GitHub release), Release workflow, SHA256SUMS.txt checksums (+5 more)

### Community 8 - "Selection"
Cohesion: 0.10
Nodes (34): io, socket, What to back up or restore., Selection, MonkeyPatch, Path, A full disk is not a file OBS holds open: the backup fails instead of skipping., Another copy of the app may finish a backup of the same name first. (+26 more)

### Community 9 - "config.py"
Cohesion: 0.11
Nodes (31): ConfigParser, contextlib, itertools, full_selection(), Everything worth keeping, except browser data (large, and rarely restored)., What to back up before restoring ``restoring``: everything a restore can…, safety_selection(), _manifest() (+23 more)

### Community 10 - "locator.py"
Cohesion: 0.15
Nodes (26): enum, psutil, config_dir_for_process(), default_config_dir(), discover(), add(), find_running_obs(), flatpak_config_dir() (+18 more)

### Community 11 - "restore.py"
Cohesion: 0.16
Nodes (25): RestoreResult, _apply(), _check_fits(), _empty(), _hardware_encoders(), _is_linked_folder(), _move(), Path (+17 more)

### Community 12 - "MonkeyPatch"
Cohesion: 0.14
Nodes (15): OSError, on_windows(), fixture, MonkeyPatch, skipif, Apply Windows' file name rules, whatever OS the tests run on., ``os.replace`` fails for files unpacked to the restore's temporary folder., On Linux, "C:/m/logo.png" is a relative path: it must not count as present. (+7 more)

### Community 13 - "Backup Selection Checkbox Tree"
Cohesion: 0.16
Nodes (16): Backup Selection Checkbox Tree, Back up Tab, Browser Source & Dock Data (Cookies, Logins), Create Backup Button, General Settings (global.ini, user.ini, Plugin Manager), Include Media Files Used by Scenes Option, Language Menu (Localization), OBS Backup & Restore Main Window (Screenshot) (+8 more)

### Community 14 - "Backup & Restore for OBS"
Cohesion: 0.09
Nodes (21): A plugin is missing after restoring, After restoring on another PC, OBS says an encoder is missing, AI disclosure, Backup file format, Backup & Restore for OBS, Can I move my setup from Windows to Linux, or the other way round?, Contributing, Download (+13 more)

### Community 15 - "tr"
Cohesion: 0.21
Nodes (10): QWidget, show_about(), format_size(), open_folder(), Show a folder in the system file manager., current_language(), The text for ``key`` in the current language, with ``{placeholders}`` filled in., set_language() (+2 more)

### Community 16 - "create.py"
Cohesion: 0.15
Nodes (20): BinaryIO, datetime, errno, platform, _add_complete_file(), _add_media_file(), _chunks(), _compression() (+12 more)

### Community 17 - "craft_backup"
Cohesion: 0.16
Nodes (18): _files(), parametrize, A path that stays inside the config folder but leaves the selected profile., On Windows, zipfile reads "a\\b/basic.ini" as "a/b/basic.ini": a file of "a"., zipfile cuts such a name short, which would restore "a" for "a\\0../../evil"., test_crafted_profile_name_cannot_delete_config(), test_files_of_a_linux_profile_with_backslash_stay_out_of_other_profiles(), test_incomplete_safety_backup_stops_the_restore() (+10 more)

### Community 18 - "collect.py"
Cohesion: 0.23
Nodes (14): browser_files(), _children(), collect_files(), walk(), _is_browser_cache_dir(), _is_browser_skip_file(), Path, Work out which files a backup should contain. (+6 more)

### Community 19 - "support.py"
Cohesion: 0.15
Nodes (17): struct, Such a link (Chromium leaves some after a crash) holds nothing to lose., test_damaged_member_leaves_config_untouched(), test_failed_restore_names_the_safety_backup(), test_link_where_the_backup_has_a_file_stops_before_any_change(), test_link_whose_target_is_gone_does_not_stop_the_restore(), test_linked_folder_inside_a_profile_survives_the_restore(), test_restore_into_linked_profile_folder() (+9 more)

### Community 21 - "GNU General Public License v2"
Cohesion: 0.40
Nodes (6): GNU General Public License v3, GNU Lesser General Public License v3, PyInstaller Bootloader Exception, GNU General Public License v2, PyInstaller licensing terms, PyInstaller run-time hooks (Apache 2.0)

### Community 22 - "RELEASE_NOTES_TEMPLATE.md"
Cohesion: 0.50
Nodes (3): AI disclosure, Download, Licenses

### Community 23 - "_FailsHalfway"
Cohesion: 0.29
Nodes (4): _FailsHalfway, Any, A file that gives some data, then fails (as a region OBS holds locked would)., open_()

### Community 26 - "_Plan"
Cohesion: 0.22
Nodes (10): _holds(), _is_selected(), members_for(), _Plan, What a restore will do, worked out and checked before anything changes., Whether any of the config paths ``rels`` is inside ``folder``., Check every path and scene collection the restore will write., Whether a file at ``rel`` (relative to the config folder) belongs to ``sel``. (+2 more)

### Community 27 - "LicensesDialog"
Cohesion: 0.29
Nodes (4): QDialog, QUrl, LicensesDialog, QWidget

### Community 28 - "FolderEdit"
Cohesion: 0.29
Nodes (7): absolute_path(), Path, ``text`` as a path, or None if it is empty or relative. A relative path would…, FolderEdit, Path, QWidget, A folder path with a “Browse…” button. Emits ``changed`` when the user edits…

### Community 29 - "i18n/__init__.py"
Cohesion: 0.18
Nodes (9): collections_abc, locale, Errors raised while creating or restoring backups. Each error names its message…, Checkable tree of the things a backup can hold., German texts (Deutsch)., English texts. This is the reference language: every key must exist here.…, preview_list(), UI texts and the current language. Each language lives in its own module… (+1 more)

### Community 30 - "BackupError"
Cohesion: 0.20
Nodes (9): BackupError, IncompleteSafetyBackupError, BaseException, Exception, Path, A backup could not be created or restored. A param that is an exception (the…, A restore failed; ``safety_backup`` holds the config folder as it was before., The safety backup could not read every file, so the restore did not start.… (+1 more)

### Community 31 - "walk"
Cohesion: 0.40
Nodes (6): DirEntry, _is_file(), _is_real_folder(), A folder that is not a link to one (symlink or junction)., A regular file, or a link to one., walk()

### Community 32 - "manifest.py"
Cohesion: 0.23
Nodes (18): is_impossible_name(), is_plain_name(), Whether ``name`` is one file or folder name on this OS, safe to join to a…, Whether no OS has a file or folder called ``name`` (``..``, ``a/b``)., _damaged(), _flag(), _is_int(), _list() (+10 more)

### Community 33 - "test_i18n.py"
Cohesion: 0.06
Nodes (41): app_version(), copy_python_license(), main(), Path, Build the standalone app with PyInstaller. uv run python packaging/build.py…, Version resource (file properties → Details) for the Windows .exe. The numeric…, The license of the Python being bundled; it lists that build's own libraries.…, write_windows_version_info() (+33 more)

### Community 34 - "error_message"
Cohesion: 0.29
Nodes (6): describe(), The message of an error that is not one of ours (an OSError, a zip error)., error_message(), BaseException, The message of ``error`` for the user: in their language if the app raised it., BaseException

### Community 35 - "test_manifest.py"
Cohesion: 0.11
Nodes (27): json, MonkeyPatch, parametrize, Path, skipif, Reading manifests and listing backups., A backup from Linux stays usable on Windows, without what Windows can't hold., test_backslash_separates_names_only_on_windows() (+19 more)

### Community 36 - "TaskRunner"
Cohesion: 0.16
Nodes (9): BackupTab, Path, QWidget, Count the media in the background: checking paths can be slow (network drives)., Show the contents of the currently selected OBS config folder., “Select all” and “Select none” buttons for a tree., selection_buttons(), Runs one task at a time and reports its progress in the GUI thread. (+1 more)

### Community 37 - "os"
Cohesion: 0.18
Nodes (11): os, file_name(), File name of a path that may come from another OS., MonkeyPatch, Path, skipif, Finding media file paths in scene collections., test_file_name_cross_os() (+3 more)

### Community 38 - "InstallPanel"
Cohesion: 0.20
Nodes (7): QGroupBox, InstallPanel, Path, QWidget, Check whether OBS is running and show it, with the OBS version., Lists the OBS config folders found and checks regularly whether OBS is running., Look for OBS installations again.

### Community 39 - "create_backup"
Cohesion: 0.21
Nodes (12): create_backup(), default_backup_name(), new_backup_path(), _part(), _printable(), _publish(), Path, Progress (+4 more)

### Community 40 - "media.py"
Cohesion: 0.29
Nodes (11): dump_scene_json(), find_media_files(), iter_strings(), load_scene_json(), looks_like_local_path(), Any, Path, Find and rewrite the local file paths that scene collections refer to. Sources… (+3 more)

### Community 41 - "backup/__init__.py"
Cohesion: 0.24
Nodes (9): dataclasses, Backup files: what goes into them, creating them and restoring them. -…, ProfileEntry, SceneCollectionEntry, BackupResult, MediaRef, Data passed into and returned from backup and restore., A media file a scene collection refers to. (+1 more)

### Community 42 - "_plan_media"
Cohesion: 0.32
Nodes (8): _crc32(), _has_contents(), _plan_media(), ZipInfo, Whether the file at ``path`` holds exactly the zip member ``info``., Where to put the media file ``info`` in ``media_dir``. A file that already…, Media files to extract, the path rewrites for the scene collections, and the…, unique_media_target()

### Community 43 - "layout.py"
Cohesion: 0.33
Nodes (6): ntpath, can_create(), creatable_name(), Layout of a backup file. A backup is a plain zip file:: manifest.json what the…, Whether this OS allows every name in ``rel`` (a ``/``-separated path). A backup…, ``name``, changed where needed so that this OS can create a file with it.

### Community 44 - "_frozen"
Cohesion: 0.50
Nodes (4): frozendict, K, _frozen(), V

## Knowledge Gaps
- **32 isolated node(s):** `backup-restore-for-obs`, `Download`, `AI disclosure`, `Licenses`, `graphify` (+27 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 269 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Selection` connect `Selection` to `manifest.py`, `test_manifest.py`, `test_restore.py`, `SelectionTree`, `create_backup`, `config.py`, `backup/__init__.py`, `restore.py`, `_plan_media`, `MonkeyPatch`, `create.py`, `craft_backup`, `collect.py`, `support.py`, `_Plan`, `i18n/__init__.py`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Why does `tr()` connect `tr` to `main_window.py`, `error_message`, `test_main_window.py`, `TaskRunner`, `RestoreTab`, `InstallPanel`, `SelectionTree`, `LicensesDialog`, `FolderEdit`, `i18n/__init__.py`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Why does `AppSettings` connect `test_main_window.py` to `main_window.py`, `test_i18n.py`, `RestoreTab`, `TaskRunner`, `InstallPanel`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 68 inferred relationships involving `Selection` (e.g. with `collect_files()` and `safety_selection()`) actually correct?**
  _`Selection` has 68 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `MainWindow` (e.g. with `BackupTab` and `InstallPanel`) actually correct?**
  _`MainWindow` has 22 INFERRED edges - model-reasoned connections that need verification._
- **What connects `backup-restore-for-obs`, `Download`, `AI disclosure` to the rest of the system?**
  _32 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `LatestCall` be split into smaller, more focused modules?**
  _Cohesion score 0.07682926829268293 - nodes in this community are weakly interconnected._