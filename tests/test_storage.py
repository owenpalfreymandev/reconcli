import app.services.storage as storage


def isolate_storage(tmp_path, monkeypatch):
    atlas_dir = tmp_path / ".atlas"
    monkeypatch.setattr(storage, "ATLAS_DIR", atlas_dir)
    monkeypatch.setattr(storage, "CONFIG_FILE", atlas_dir / "config.json")
    return atlas_dir


def test_token_round_trip_and_missing_file(tmp_path, monkeypatch):
    isolate_storage(tmp_path, monkeypatch)
    assert storage.get_token() is None
    storage.save_token("secret")
    assert storage.get_token() == "secret"


def test_clear_token_is_idempotent_and_removes_file(tmp_path, monkeypatch):
    isolate_storage(tmp_path, monkeypatch)
    storage.clear_token()
    storage.save_token("secret")
    storage.clear_token()
    assert storage.get_token() is None
    storage.clear_token()


def test_save_creates_atlas_directory(tmp_path, monkeypatch):
    atlas_dir = isolate_storage(tmp_path, monkeypatch)
    storage.save_token("secret")
    assert atlas_dir.is_dir()
