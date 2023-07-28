from lumina.config import Settings, settings


def test_root_path_none_when_no_stage():
    assert settings.root_path is None


def test_root_path_proxied_when_prod():
    settings = Settings(stage_name="prod")
    assert settings.root_path == "https://lumina.nthp.wjdp.uk"


def test_root_path_is_stage_otherwise():
    settings = Settings(stage_name="wjdp")
    assert settings.root_path == "/wjdp"
