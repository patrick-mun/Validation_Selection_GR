from genorun_validation.config import load_config


def test_import_config():
    assert callable(load_config)
