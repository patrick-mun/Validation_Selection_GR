from __future__ import annotations

from pathlib import Path

import pytest
from web import create_app


def test_dashboard_phase0_renders_operational_layout(monkeypatch, tmp_path: Path):
    """Vérifie que le tableau de bord phase 0 reste servi par Flask."""
    monkeypatch.setenv("GENORUN_ENABLE_DATABASE", "false")
    monkeypatch.setenv("GENORUN_RUNS_ROOT", str(tmp_path / "runs"))

    app = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Validation de la sélection WGS" in html
    assert "Projection PCA" in html
    assert "ADMIXTURE (K=4)" in html
    assert "Logs &amp; traçabilité" in html
    assert "Données de démonstration" in html


def test_dashboard_phase0_can_create_and_poll_job(monkeypatch, tmp_path: Path):
    """Vérifie que la refonte visuelle ne casse pas le flux job existant."""
    monkeypatch.setenv("GENORUN_ENABLE_DATABASE", "false")
    monkeypatch.setenv("GENORUN_RUNS_ROOT", str(tmp_path / "runs"))

    app = create_app()
    client = app.test_client()

    create_response = client.post(
        "/api/jobs",
        json={
            "dataset": "1000G_chr22",
            "profile": "profil_C",
            "strategy": "geo_ancestrale_decouverte",
        },
    )

    assert create_response.status_code == 201
    payload = create_response.get_json()
    assert payload["status"] == "queued"

    status_response = client.get(f"/api/jobs/{payload['job_id']}/status")
    status_payload = status_response.get_json()

    assert status_response.status_code == 200
    assert status_payload["job_id"] == payload["job_id"]
    assert status_payload["status"] == "queued"


@pytest.mark.parametrize(
    ("path", "title"),
    [
        ("/configuration", "Configuration"),
        ("/donnees", "Données"),
        ("/qc", "QC"),
        ("/pca", "PCA"),
        ("/admixture", "ADMIXTURE"),
        ("/king-ibd", "KING/IBD"),
        ("/roh", "ROH"),
        ("/selection-wgs", "Sélection WGS"),
        ("/imputation", "Imputation"),
        ("/rapport", "Rapport"),
    ],
)
def test_theme_pages_render_placeholder_workspace(monkeypatch, tmp_path: Path, path: str, title: str):
    """Vérifie que chaque item de navigation ouvre une page Flask dédiée."""
    monkeypatch.setenv("GENORUN_ENABLE_DATABASE", "false")
    monkeypatch.setenv("GENORUN_RUNS_ROOT", str(tmp_path / "runs"))

    app = create_app()
    client = app.test_client()

    response = client.get(path)

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert f"<h1>{title}</h1>" in html
    assert f"<h2>{title}</h2>" in html
    assert "Phase 0 — structure UI" in html
    assert "Le contenu détaillé sera ajouté" in html
