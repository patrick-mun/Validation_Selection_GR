from __future__ import annotations

from pathlib import Path

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
