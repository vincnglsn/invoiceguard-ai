import subprocess, os, sys, time

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
