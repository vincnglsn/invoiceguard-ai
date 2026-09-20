# InvoiceGuard AI — Démarrage automatique Windows
# Configure le démarrage automatique au boot via le Planificateur de tâches Windows
# Exécutez ce script UNE SEULE FOIS en tant qu'Administrateur

$ErrorActionPreference = "SilentlyContinue"

$ProjectDir = "c:\Users\PC-FAMILY-N6\.gemini\antigravity\scratch\agence_ia"
$PythonExe  = (Get-Command python).Source
$TaskName   = "InvoiceGuardAI"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  InvoiceGuard AI — Configuration demarrage automatique" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Supprime l'ancienne tâche si elle existe
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false 2>$null

# Crée le script de lancement
$LauncherScript = @"
import subprocess, os, time, sys

PROJECT = r"$ProjectDir"
os.chdir(PROJECT)

# Charge l'environnement
from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT, '.env'))

apps = [
    ("invoiceguard_app.py",        8502, "Dashboard principal"),
    ("invoiceguard_prospecteur.py", 8503, "Prospecteur"),
    ("invoiceguard_paiements.py",   8504, "Paiements"),
    ("invoiceguard_partenaire_ec.py", 8506, "Espace EC"),
    ("invoiceguard_pricing.py",     8507, "Pricing Stripe"),
    ("invoiceguard_fondateur.py",   8508, "Dashboard Fondateur"),
    ("invoiceguard_guide.py",       8509, "Guide Lead Magnet"),
    ("planificateur_marketing.py",  8510, "Planificateur"),
]

procs = []
for script, port, nom in apps:
    p = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", script, "--server.port", str(port), "--server.headless", "true"],
        cwd=PROJECT,
    )
    procs.append(p)
    print(f"[OK] {nom} -> http://localhost:{port}")
    time.sleep(1.5)

# Lance le serveur landing page
lp = subprocess.Popen([sys.executable, "serveur_landing.py", "--port", "8000"], cwd=PROJECT)
print("[OK] Landing page -> http://localhost:8000")
time.sleep(1)

# Lance le tunnel Cloudflare
cf = subprocess.Popen(["cloudflared", "tunnel", "--url", "http://localhost:8502"],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
print("[OK] Cloudflare tunnel demarre...")

# Ecrit le log de demarrage
with open(os.path.join(PROJECT, "startup.log"), "a") as f:
    from datetime import datetime
    f.write(f"{datetime.now()} - InvoiceGuard AI demarre (tous les services)\n")

# Garde vivant
for p in procs + [lp, cf]:
    try:
        p.wait()
    except KeyboardInterrupt:
        p.terminate()
"@

$LauncherPath = "$ProjectDir\auto_startup.py"
$LauncherScript | Out-File -FilePath $LauncherPath -Encoding utf8
Write-Host "  [OK] Script de lancement cree : $LauncherPath" -ForegroundColor Green

# Configure la tache planifiee Windows
$Action  = New-ScheduledTaskAction -Execute $PythonExe -Argument $LauncherPath -WorkingDirectory $ProjectDir
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -RunLevel Highest `
    -Description "InvoiceGuard AI — Lance toutes les apps au demarrage" `
    -Force | Out-Null

Write-Host "  [OK] Tache planifiee '$TaskName' creee (au demarrage de session)" -ForegroundColor Green

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Configuration terminee !" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Apps qui demarreront automatiquement au prochain login :"
Write-Host "    http://localhost:8502  Dashboard principal"
Write-Host "    http://localhost:8506  Espace Expert-Comptable"
Write-Host "    http://localhost:8507  Pricing Stripe"
Write-Host "    http://localhost:8508  Dashboard Fondateur"
Write-Host "    http://localhost:8509  Guide Lead Magnet"
Write-Host "    http://localhost:8510  Planificateur Marketing"
Write-Host "    http://localhost:8000  Landing Page"
Write-Host ""
Write-Host "  Pour tester maintenant :"
Write-Host "    python auto_startup.py"
Write-Host ""
