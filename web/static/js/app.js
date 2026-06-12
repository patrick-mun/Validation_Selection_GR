// Front vanilla : soumission du lancement + polling du statut. Aucune dépendance.
"use strict";

async function lancerAnalyse() {
  const body = {
    dataset: document.getElementById("dataset").value,
    profile: document.getElementById("profile").value,
    strategy: document.getElementById("strategy").value,
  };
  const btn = document.getElementById("btn-lancer");
  btn.disabled = true;
  try {
    const res = await fetch("/api/jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok) {
      alert("Erreur : " + (data.error || res.status));
      return;
    }
    suivreJob(data.job_id);
  } finally {
    btn.disabled = false;
  }
}

// Interroge l'état du job toutes les 2 s jusqu'à un état terminal.
function suivreJob(jobId) {
  const out = document.getElementById("suivi");
  const terminaux = ["completed", "failed", "cancelled"];
  const tick = async () => {
    const res = await fetch(`/api/jobs/${jobId}/status`);
    if (!res.ok) {
      out.textContent = "Job introuvable.";
      return;
    }
    const j = await res.json();
    out.innerHTML = `Run <a href="/runs/${j.job_id}">${j.job_id}</a> — ` +
      `<span class="badge s-${j.status}">${j.status}</span> ${j.message || ""}`;
    if (!terminaux.includes(j.status)) {
      setTimeout(tick, 2000);
    }
  };
  tick();
}

document.addEventListener("DOMContentLoaded", () => {
  const b = document.getElementById("btn-lancer");
  if (b) b.addEventListener("click", lancerAnalyse);
});
