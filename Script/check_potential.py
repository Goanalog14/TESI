import os
import csv
import difflib

pathcsv = "/home/simone/Scaricati/my_report.csv"
path_set_virus = "/home/simone/Scrivania/set_virus/set_virus"  

def save_from_report():
    with open("virus_da_report",mode="w",newline='') as v:
        with open(pathcsv,mode="r") as r:
            reader = csv.reader(r)
            for row in reader:
                nome_virus = row[3].split('/')
                v.write(nome_virus[-1]+'\n')

def save_from_set_virus():
    with open("virus_da_set", mode="w", newline='') as v:
        lista = os.listdir(path_set_virus)
        for file in lista:
            v.write(file+'\n')

def save_unchecked():
    list_report = []
    c = 0

    # Leggi le stringhe da 'virus_da_report'
    with open('virus_da_report', mode="r", newline='') as r:
        list_report = [row.strip() for row in r.readlines()]

    # Leggi le stringhe da 'virus_da_set'
    with open('virus_da_set', mode="r", newline='') as v:
        virus_set = [row.strip() for row in v.readlines()]
    
    # Trova le righe di 'virus_da_set' non presenti in 'virus_da_report'
    missing_rows = [virus for virus in virus_set if virus not in list_report]

    # Salva in un file le righe mancanti
    if missing_rows:
        print("Le seguenti righe sono presenti in 'virus_da_set' ma non in 'virus_da_report':")
        with open('possible_virus',mode="w",newline='') as pv:
            for row in missing_rows:
                pv.write(row + '\n')
                print(row)
                c += 1
    else:
        print("Tutte le righe di 'virus_da_set' sono presenti anche in 'virus_da_report'.")
    print(f"Numero possibili virus: {c}")

           


#salva da report i virus trovati da eset object URI -- 3
#save_from_report()
#save_from_set_virus()
save_unchecked()