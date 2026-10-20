"""Cross-platform generated-documentation regression tests by Jason Stys.

Functions: test_portable_inventory_order. Variables: temporary sources and expected ordering.
Exact lines: docs/CODE_INDEX.md. Temporary files are test fixtures, never executed.
"""

import pytest

from tools import verify_repo


def test_portable_inventory_order(tmp_path, monkeypatch):
    """String ordering is identical on Windows and case-sensitive filesystems."""
    monkeypatch.setattr(verify_repo, "ROOT", tmp_path)
    monkeypatch.setattr(verify_repo, "listed_paths", lambda: ["a.py", "B.py", "README.md"])
    (tmp_path / "a.py").write_text('"""Fixture by Jason Stys."""\n', encoding="utf-8")
    (tmp_path / "B.py").write_text('"""Fixture by Jason Stys."""\n', encoding="utf-8")
    (tmp_path / "README.md").write_text("# Fixture\n", encoding="utf-8")
    assert [path.name for path in verify_repo.source_files()] == ["B.py", "README.md", "a.py"]
    _, catalog = verify_repo.inventory()
    assert catalog.index("`B.py`") < catalog.index("`README.md`") < catalog.index("`a.py`")


def test_configuration_purposes(tmp_path, monkeypatch):
    """Structured configuration gets a human explanation instead of a meaningless brace."""
    monkeypatch.setattr(verify_repo, "ROOT", tmp_path)
    monkeypatch.setattr(verify_repo, "listed_paths", lambda: ["package.json"])
    (tmp_path / "package.json").write_text("{}\n", encoding="utf-8")
    _, catalog = verify_repo.inventory()
    assert "Pinned browser dependencies" in catalog


def test_private_files_never_enter_catalog(tmp_path, monkeypatch):
    """Even accidentally tracked private formats are not read or copied into documentation."""
    monkeypatch.setattr(verify_repo, "ROOT", tmp_path)
    monkeypatch.setattr(
        verify_repo, "listed_paths", lambda: ["README.md", ".env", "account.key", "history.sqlite3"]
    )
    for name in ("README.md", ".env", "account.key", "history.sqlite3"):
        (tmp_path / name).write_text(
            "public" if name == "README.md" else "PRIVATE_SENTINEL", encoding="utf-8"
        )
    _, catalog = verify_repo.inventory()
    assert "PRIVATE_SENTINEL" not in catalog
    assert [p.name for p in verify_repo.source_files()] == ["README.md"]


def test_inventory_path_confinement(tmp_path, monkeypatch):
    """A malformed listed path cannot read outside the repository root."""
    monkeypatch.setattr(verify_repo, "ROOT", tmp_path)
    monkeypatch.setattr(verify_repo, "listed_paths", lambda: ["../outside.txt"])
    with pytest.raises(ValueError, match="leave its repository"):
        verify_repo.source_files()
