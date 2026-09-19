import urllib.request
import urllib.parse
import json
import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # ne doit pas être accessible, juste pour avoir la route locale
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def send_telegram_message():
    bot_token = "8907736815:AAHFLmKEglxfHK5SOoXy94Obbo_Ufyc3APo"
    chat_id = "6020342344"
    
    ip = get_local_ip()
    url_app = f"http://{ip}:8501"
    url_local = "http://localhost:8501"
    
    message = f"""🚀 [AGENCE IA] Votre Démonstrateur est 100% opérationnel !

L'application a été codée et lancée en arrière-plan.
Vous pouvez montrer ça à vos clients dès maintenant.

Lien local (sur votre PC) :
{url_local}

Si vous êtes sur le même réseau Wifi avec votre téléphone, essayez ce lien :
{url_app}

Fermez cette appli depuis le terminal du PC quand vous avez terminé."""

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = urllib.parse.urlencode({'chat_id': chat_id, 'text': message}).encode('utf-8')
    req = urllib.request.Request(url, data=data)
    
    try:
        with urllib.request.urlopen(req) as response:
            res = response.read()
            print("Message Telegram envoyé avec succès.")
    except Exception as e:
        print(f"Erreur d'envoi Telegram : {e}")

if __name__ == "__main__":
    send_telegram_message()
