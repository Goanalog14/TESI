
import os

source_dir = "/home/kali/Virus/set_virus"
dest_dir = "/home/kali/Virus/exe_virus"
#apri e leggi possible_virus
with open("possible_virus",mode="r",newline='') as pv:
    possible_virus = [file.strip() for file in pv.readlines()]
for file in possible_virus:
    filepath = os.path.join(source_dir,file)
    if os.path.exists(filepath):
        #copia i possible_virus in exe_virus
        os.system(f"cp {filepath} {dest_dir}")
