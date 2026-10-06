"""VoiceStudio 本机音色：目录解析、断线行为与 /audio/speech 调用契约，不依赖真实服务。"""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import requests

from app.config import config
from app.services import voice


@pytest.fixture
def voicestudio_config(monkeypatch):
    settings = {"base_url": "http://127.0.0.1:3900/v1/", "model_id": "voxcpm2"}
    monkeypatch.setattr(config, "voicestudio", settings)
    return settings


def test_voice_list_offers_saved_profiles_by_name(monkeypatch, voicestudio_config):
    payload = {"voices": [
        {"voice_id": "alloy", "name": "Alloy", "type": "openai_alias"},
        {"voice_id": "f9c08f52", "name": "khmer-voice-artist", "type": "profile"},
        {"voice_id": "demo0001", "name": "", "type": "profile"},
        {"voice_id": "", "name": "broken", "type": "profile"},
        "not-a-voice",
    ]}
    get = Mock(return_value=SimpleNamespace(status_code=200, json=lambda: payload))
    monkeypatch.setattr(voice.requests, "get", get)
    assert voice.get_voicestudio_voices() == {
        "voicestudio:f9c08f52": "khmer-voice-artist",
        "voicestudio:demo0001": "demo0001",
    }
    get.assert_called_once_with("http://127.0.0.1:3900/v1/audio/voices", timeout=5)


def test_missing_config_uses_local_default(monkeypatch):
    monkeypatch.setattr(config, "voicestudio", {})
    get = Mock(return_value=SimpleNamespace(status_code=200, json=lambda: {"voices": []}))
    monkeypatch.setattr(voice.requests, "get", get)
    assert voice.get_voicestudio_voices() == {}
    assert get.call_args.args[0] == f"{voice.VOICESTUDIO_DEFAULT_BASE_URL}/audio/voices"


@pytest.mark.parametrize("failure", [requests.Timeout(), requests.ConnectionError(),
                                     ValueError("invalid JSON"), 500, ["list"], {"voices": None}])
def test_voice_list_failure_is_empty(monkeypatch, voicestudio_config, failure):
    if isinstance(failure, Exception):
        get = Mock(side_effect=failure)
    else:
        get = Mock(return_value=SimpleNamespace(
            status_code=failure if isinstance(failure, int) else 200,
            json=lambda: failure,
        ))
    monkeypatch.setattr(voice.requests, "get", get)
    assert voice.get_voicestudio_voices() == {}


def test_tts_sends_profile_id_with_pinned_engine_and_long_timeout(monkeypatch, voicestudio_config, tmp_path):
    post = Mock(return_value=SimpleNamespace(status_code=200, content=b"audio", text=""))
    monkeypatch.setattr(voice.requests, "post", post)
    monkeypatch.setattr(voice, "AudioFileClip", Mock(return_value=Mock(duration=2.0)))
    output = tmp_path / "output.mp3"
    maker = voice.tts("សួស្ដីបងប្អូន", "voicestudio:f9c08f52", 1.0, str(output))
    assert maker is not None
    assert output.read_bytes() == b"audio"
    assert post.call_args.args[0] == "http://127.0.0.1:3900/v1/audio/speech"
    assert post.call_args.kwargs["json"] == {
        "model": "voxcpm2", "input": "សួស្ដីបងប្អូន", "voice": "f9c08f52",
        "response_format": "mp3", "speed": 1.0,
    }
    assert "Authorization" not in post.call_args.kwargs["headers"]
    assert post.call_args.kwargs["timeout"] == voice.VOICESTUDIO_TTS_TIMEOUT_SECONDS


def test_other_providers_keep_the_short_timeout(monkeypatch, tmp_path):
    post = Mock(return_value=SimpleNamespace(status_code=200, content=b"audio", text=""))
    monkeypatch.setattr(voice.requests, "post", post)
    monkeypatch.setattr(voice, "AudioFileClip", Mock(return_value=Mock(duration=1.0)))
    assert voice._openai_compatible_tts("kokoro", "http://localhost/v1", "", "kokoro",
                                        "af_heart", "Hello", 1, str(tmp_path / "a.mp3"))
    assert post.call_args.kwargs["timeout"] == 120


@pytest.mark.parametrize("voice_name, text", [
    ("voicestudio:f9c08f52", "...!!!"),
    ("voicestudio:", "Hello"),
])
def test_unusable_requests_are_not_sent(monkeypatch, voicestudio_config, tmp_path, voice_name, text):
    post = Mock()
    monkeypatch.setattr(voice.requests, "post", post)
    assert voice.tts(text, voice_name, 1.0, str(tmp_path / "a.mp3")) is None
    post.assert_not_called()
