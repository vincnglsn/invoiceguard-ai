"""
InvoiceGuard AI — Tunnel Public Automatique
Expose l'app locale sur Internet sans configuration Ngrok manuelle.
Alternative : utilise localtunnel (aucun compte requis).
"""
import subprocess
import sys
import time
import re
import urllib.request

def expose_with_localtunnel(port: int = 8502) -> str:
    """
    Crée un tunnel public via localtunnel.me (aucun compte requis).
    Nécessite Node.js + npx.
    """
    try:
        proc = subprocess.Popen(
            ["npx", "localtunnel", "--port", str(port), "--subdomain", "invoiceguard-demo"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        for line in proc.stdout:
            if "https://" in line:
                url = line.strip()
                return url
    except Exception as e:
        return f"Erreur localtunnel: {e}"
    return ""


def expose_with_pyngrok(port: int = 8502) -> str:
    """
    Crée un tunnel ngrok (nécessite un compte ngrok gratuit et le token).
    """
    try:
        from pyngrok import ngrok
        tunnel = ngrok.connect(port, "http")
        return tunnel.public_url
    except Exception as e:
        return f"Erreur ngrok: {e}"


if __name__ == "__main__":
    port = 8502
    print(f"\n🔗 Création du tunnel public pour http://localhost:{port}...")
    print("Méthode 1 : pyngrok (recommandé)...")
    
    url = expose_with_pyngrok(port)
    if url.startswith("http"):
        print(f"\n✅ URL PUBLIQUE : {url}")
        print(f"\nPartagez ce lien pour montrer InvoiceGuard en démo live !")
        print("Ctrl+C pour couper le tunnel.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nTunnel fermé.")
    else:
        print(f"⚠️  {url}")
        print("\nConfigurer votre token Ngrok :")
        print("1. Créez un compte gratuit sur https://ngrok.com")
        print("2. Récupérez votre token dans https://dashboard.ngrok.com/get-started/your-authtoken")
        print(f'3. Lancez : python -c "from pyngrok import ngrok; ngrok.set_auth_token(\'VOTRE_TOKEN\')"')
        print("4. Relancez ce script")
