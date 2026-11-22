"""Reading profiles, scene collections and the OBS version."""

from pathlib import Path

import pytest

from obs_backup.obs import config as obs_config

from support import write


def test_reads_config(obs: Path) -> None:
    assert [(p.name, p.dir_name) for p in obs_config.list_profiles(obs)] == [
        ("Twitch Stream", "Twitch_Stream"),
        ("Unbenannt", "Unbenannt"),
    ]
    assert [(s.name, s.file_name) for s in obs_config.list_scene_collections(obs)] == [
        ("Main Scenes", "Main.json"),
        ("Other", "Other.json"),
    ]
    assert obs_config.obs_version(obs) == "33.0.1"
    assert (
        obs_config.has_plugin_config(obs)
        and obs_config.has_browser_data(obs)
        and not obs_config.has_plugins(obs)
    )


def test_general_settings_found_by_any_of_their_parts(tmp_path: Path) -> None:
    assert not obs_config.has_global_settings(tmp_path)
    (tmp_path / "plugin_manager").mkdir()  # no global.ini or user.ini yet
    assert obs_config.has_global_settings(tmp_path)


@pytest.mark.parametrize(
    ("ini", "encoders", "hardware"),
    [
        # Advanced mode: the stream encoder and a recording encoder of its own
        (
            "[Output]\nMode=Advanced\n[AdvOut]\nEncoder=obs_nvenc_av1_tex\nRecEncoder=ffmpeg_nvenc\n",
            ["obs_nvenc_av1_tex", "ffmpeg_nvenc"],
            ["NVIDIA NVENC"],
        ),
        # "none": recording uses the stream encoder
        (
            "[Output]\nMode=Advanced\n[AdvOut]\nEncoder=h264_texture_amf\nRecEncoder=none\n",
            ["h264_texture_amf"],
            ["AMD AMF"],
        ),
        # custom FFmpeg recording doesn't use RecEncoder
        (
            "[Output]\nMode=Advanced\n[AdvOut]\nEncoder=obs_x264\nRecType=FFmpeg\nRecEncoder=obs_qsv11\n",
            ["obs_x264"],
            [],
        ),
        # Simple mode, recording "same as stream": RecEncoder isn't used
        (
            "[SimpleOutput]\nStreamEncoder=x264\nRecQuality=Stream\nRecEncoder=nvenc\n",
            ["x264"],
            [],
        ),
        (
            "[Output]\nMode=Simple\n[SimpleOutput]\nStreamEncoder=qsv\nRecQuality=HQ\nRecEncoder=amd_hevc\n",
            ["qsv", "amd_hevc"],
            ["Intel Quick Sync", "AMD AMF"],
        ),
        # Advanced settings stay in basic.ini after switching back to Simple mode
        (
            "[Output]\nMode=Simple\n[SimpleOutput]\nStreamEncoder=x264\n[AdvOut]\nEncoder=jim_nvenc\n",
            ["x264"],
            [],
        ),
        # nothing set yet: OBS chooses
        ("[General]\nName=New\n", [], []),
    ],
)
def test_profile_encoders(
    tmp_path: Path, ini: str, encoders: list[str], hardware: list[str]
) -> None:
    write(tmp_path / "basic.ini", ini)
    assert obs_config.profile_encoders(tmp_path) == encoders
    assert obs_config.hardware_encoders(tmp_path) == hardware
