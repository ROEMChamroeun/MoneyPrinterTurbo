"""运行实际 Streamlit 页面，验证 VoiceStudio 音色以名称显示、断线时保留选择。"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from streamlit.testing.v1 import AppTest

from app.config import config
from app.services import voice

VOICES = {"voicestudio:demo0001": "VoiceStudio Demo Voice",
          "voicestudio:f9c08f52": "khmer-voice-artist"}


@pytest.fixture
def ui(monkeypatch):
    monkeypatch.setattr(config, "ui", dict(config.ui, voice_mode="tts", tts_server="voicestudio",
                                          voice_name="voicestudio:f9c08f52"))
    monkeypatch.setattr(config, "voicestudio", dict(base_url="http://127.0.0.1:3900/v1",
                                                   model_id="voxcpm2"))
    monkeypatch.setattr(config, "save_config", Mock())
    monkeypatch.setattr(config, "try_save_config", Mock(return_value=True))
    page = AppTest.from_file(str(Path(__file__).parents[2] / "webui/Main.py"), default_timeout=30)
    page.session_state["ui_language"] = "en"
    return page


def selected_voice(page):
    return next(item for item in page.selectbox
                if str(item.key).startswith("speech_synthesis_select_voicestudio"))


def test_saved_voices_show_names_and_keep_the_saved_one(monkeypatch, ui):
    monkeypatch.setattr(voice, "get_voicestudio_voices", Mock(return_value=dict(VOICES)))
    ui.run()
    box = selected_voice(ui)
    assert box.options == ["VoiceStudio Demo Voice", "khmer-voice-artist"]
    assert box.value == "voicestudio:f9c08f52"
    assert config.ui["voice_name"] == "voicestudio:f9c08f52"
    assert not ui.exception


def test_closed_voicestudio_keeps_selection_and_says_what_to_do(monkeypatch, ui):
    get = Mock(side_effect=[{}, dict(VOICES)])
    monkeypatch.setattr(voice, "get_voicestudio_voices", get)
    ui.run()
    assert selected_voice(ui).value == "voicestudio:f9c08f52"
    assert config.ui["voice_name"] == "voicestudio:f9c08f52"
    assert any("Open the VoiceStudio app" in str(w.value) for w in ui.warning)
    ui.session_state["voicestudio_voice_catalog"]["checked_at"] = -100
    ui.run()
    assert selected_voice(ui).value == "voicestudio:f9c08f52"
    assert not any("Open the VoiceStudio app" in str(w.value) for w in ui.warning)
    assert get.call_count == 2
    assert not ui.exception


@pytest.mark.parametrize("model_id, disabled", [("voxcpm2", True), ("omnivoice", False)])
def test_speed_control_follows_the_engine(monkeypatch, ui, model_id, disabled):
    config.voicestudio["model_id"] = model_id
    monkeypatch.setattr(voice, "get_voicestudio_voices", Mock(return_value=dict(VOICES)))
    ui.run()
    speed = next(item for item in ui.selectbox if str(item.key).startswith("voice_rate_select"))
    assert speed.disabled is disabled
    assert not ui.exception


def test_address_change_reloads_the_voice_list(monkeypatch, ui):
    get = Mock(return_value=dict(VOICES))
    monkeypatch.setattr(voice, "get_voicestudio_voices", get)
    ui.run()
    next(item for item in ui.text_input if item.key == "voicestudio_base_url_input") \
        .set_value("http://127.0.0.1:3999/v1").run()
    assert get.call_count == 2
    assert config.voicestudio["base_url"] == "http://127.0.0.1:3999/v1"
    assert not ui.exception
