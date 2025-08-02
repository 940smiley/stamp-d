import sys, pathlib

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from config import load_config, save_config


def test_settings_roundtrip():
    cfg = load_config()
    original = cfg.get("ai_model")
    cfg["ai_model"] = "manual"
    save_config(cfg)
    new_cfg = load_config()
    assert new_cfg["ai_model"] == "manual"
    # restore
    cfg["ai_model"] = original
    save_config(cfg)
