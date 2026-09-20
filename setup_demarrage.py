"""
InvoiceGuard AI - Script de demarrage automatique
Genere la tache Windows et le lanceur Python.
"""
import subprocess
import os
import sys

PROJECT = r"c:\Users\PC-FAMILY-N6\.gemini\antigravity\scratch\agence_ia"
PYTHON  = sys.executable
TASK_NAME = "InvoiceGuardAI"

LAUNCHER = r'''import subprocess, os, sys, time

PROJECT = r"c:\Users\PC-FAMILY-N6\.gemini\antigravity\scratch\agence_ia"
os.chdir(PROJECT)

APPS = [
    ("invoiceguard_app.py", 8502),
    ("invoiceguard_prospecteur.py", 8503),
    ("invoiceguard_paiements.py", 8504),
    ("invoiceguard_partenaire_ec.py", 8506),
    ("invoiceguard_pricing.py", 8507),
    ("invoiceguard_fondateur.py", 8508),
    ("invoiceguard_guide.py", 8509),
    ("planificateur_marketing.py", 8510),
]

procs = []
for script, port in APPS:
    p = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", script,
         "--server.port", str(port), "--server.headless", "true"],
        cwd=PROJECT,
    )
    procs.append(p)
    time.sleep(1.5)

# Serveur landing page
lp = subprocess.Popen([sys.executable, "serveur_landing.py", "--port", "8000"], cwd=PROJECT)

# Cloudflare tunnel
cf = subprocess.Popen(["cloudflared", "tunnel", "--url", "http://localhost:8502"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

with open(os.path.join(PROJECT, "startup.log"), "a") as f:
    from datetime import datetime
    f.write(f"{datetime.now()} - InvoiceGuard AI started\n")

for p in procs + [lp, cf]:
    try: p.wait()
    except: p.terminate()
'''

launcher_path = os.path.join(PROJECT, "auto_startup.py")
with open(launcher_path, "w", encoding="utf-8") as f:
    f.write(LAUNCHER)
print(f"[OK] Launcher cree : {launcher_path}")

# Creer la tache Windows via schtasks.exe
cmd = [
    "schtasks", "/Create", "/F",
    "/TN", TASK_NAME,
    "/TR", f'"{PYTHON}" "{launcher_path}"',
    "/SC", "ONLOGON",
    "/RL", "HIGHEST",
    "/RU", os.environ.get("USERNAME", ""),
]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode == 0:
    print(f"[OK] Tache Windows '{TASK_NAME}' creee (demarrage au login)")
else:
    print(f"[WARN] Tache non creee (droits admin requis): {result.stderr.strip()}")
    print(f"  Pour creer manuellement, lancez en admin: python setup_demarrage.py")

print("\n[OK] Configuration terminee !")
print("  Pour tester : python auto_startup.py")
