"""Data passed into and returned from backup and restore."""

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

# progress(done, total, current item)
Progress = Callable[[int, int, str], None]


@dataclass
class Selection:
    """What to back up or restore."""

    profiles: list[str] = field(default_factory=list)  # profile folder names
    scene_collections: list[str] = field(default_factory=list)  # scene collection file names
    global_settings: bool = False
    plugin_config: bool = False
    browser_data: bool = False
    plugins: bool = False
    media: bool = False

    def is_empty(self) -> bool:
        return not (
            self.profiles
            or self.scene_collections
            or self.global_settings
            or self.plugin_config
            or self.browser_data
            or self.plugins
        )


@dataclass
class MediaRef:
    """A media file a scene collection refers to."""

    original: str  # path exactly as stored in the scene collection
    archive: str = ""  # member name in the zip
    size: int = 0
    used_by: list[str] = field(default_factory=list)  # scene collection file names


@dataclass
class BackupResult:
    path: Path
    files: int
    total_bytes: int
    skipped: list[str] = field(default_factory=list)


@dataclass
class RestoreResult:
    files: int
    media_restored: int = 0
    media_missing: list[str] = field(default_factory=list)
    # Selected files that could not be read when the backup was made, so are not in
    # it; files of those names in the config folder were left as they were.
    kept_current: list[str] = field(default_factory=list)
    safety_backup: Path | None = None
    # Restored profiles that use a hardware encoder (profile name -> kinds of encoder,
    # e.g. "NVIDIA NVENC"). On a computer without that hardware OBS reports the
    # encoder as missing until another one is chosen.
    hardware_encoders: dict[str, list[str]] = field(default_factory=dict)
