import pytest


@pytest.fixture
def tmp_fig(monkeypatch, tmp_path):
    """Point a module's module-level FIG at a temporary output path."""
    def patch(module, name="figure.json"):
        path = tmp_path / name
        monkeypatch.setattr(module, "FIG", str(path))
        return path

    return patch
