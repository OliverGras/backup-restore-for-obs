"""Reading profiles, scene collections and the OBS version."""

from pathlib import Path

from obs_backup.obs import config as obs_config


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
