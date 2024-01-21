import subprocess
import argparse
import os
import signal
from time import sleep
from datetime import datetime
import virtualbox
import csv
import paramiko




working_dir = "/home/simone/Desktop/Tesi"


#sandbox
sandbox = "eset"
sandbox_snap = "flask3_ssh"
username_sandbox = "user"
password_sandbox = "password"
dir_virus_on_server="/home/user/virus_test_eset/flask_server/virus"
url = "http://192.168.56.101:8080/uploader"
eset_csv = "eset.csv"

#analyzer
analyzer = "kali-linux"
username_analyzer = "kali"
password_analyzer = "kali"
ip_analyzer = "192.168.56.103"
porta_analyzer = 22
dir_virus="/home/kali/Virus/set_virus"

#comandi
file = "/usr/bin/file"
curl = "/usr/bin/curl"
chmod = "/usr/bin/chmod"
ls = "/usr/bin/ls"


vbox = virtualbox.VirtualBox()
vm = vbox.find_machine(sandbox)



def get_report():
    command_generate_report = f"VBoxManage guestcontrol {analyzer} run /home/kali/Virus_test_eset/get_report.py --username {username_analyzer} --password {password_analyzer} --wait-stdout"
    os.system(command_generate_report)
    
    remote_file_path = "/home/kali/Virus_test_eset/report.csv"
    local_file_path = "/home/simone/Desktop/Tesi/report.csv"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(ip_analyzer, porta_analyzer, username_analyzer, password_analyzer)
        sftp = ssh.open_sftp()
        sftp.get(remote_file_path,local_file_path)
        print(f"File copiato con successo da {remote_file_path} a {local_file_path}")
    except Exception as e:
        print(f"Errore nella connessione SSH: {str(e)}")
    finally:
            # Chiudi la connessione SSH quando hai finito
        sftp.close()
        ssh.close()



def ripristina_snap_eset(vm,headless):
    if vm.state != 0:
        subprocess.call(['VBoxManage','controlvm', sandbox,'poweroff'])
        sleep(4)
    subprocess.call(['VBoxManage', 'snapshot', sandbox, 'restore', sandbox_snap])
    if headless:
        subprocess.call(['VBoxManage', 'startvm', sandbox, "--type", "headless"])
    else:
        subprocess.call(['VBoxManage', 'startvm', sandbox])



def get_sha1(virus):
    virus_path = os.path.join(dir_virus,virus)
    sha1_command = [f"VBoxManage", "guestcontrol", analyzer, "run", "/home/kali/Virus_test_eset/sha1.py", "--username", username_analyzer, "--password", password_analyzer, "--wait-stdout","--",virus_path]
    result = subprocess.run(sha1_command,stdout = subprocess.PIPE,universal_newlines = True)
    return result.stdout.strip()
     



def get_bit(virus):
    virus_path = os.path.join(dir_virus,virus)
    file_command = [f"VBoxManage", "guestcontrol", analyzer, "run", file, "--username", username_analyzer, "--password", password_analyzer, "--wait-stdout","--",virus_path]
    result = subprocess.run(file_command,stdout = subprocess.PIPE,universal_newlines = True)
    return result.stdout.split(" ")[2]



def timeout_handler(signum, frame):
    raise TimeoutError("Execution timed out")



# GESTIONE CSV
def get_last_row(nome_csv):
    with open(nome_csv,mode='r') as f:
        reader = csv.reader(f)
        last_row = None
        for row in reader:
            last_row = row
    return last_row

def create_eset_csv(nome_csv):
    data = ['Time detected', 'Severity', 'Scanner', 'Object URI', 'Detection', 'Detection Type', 'Action', 'User', 'Application', 'Circumstances', 'Hash', 'Raw detection name']
    with open(nome_csv,"w") as r:
        writer = csv.writer(r)
        writer.writerow(data)

def create_csv_virus(nome_csv):
    data = ['Date','Hash','Filename','Result']
    with open(nome_csv,"w") as r:
        writer = csv.writer(r)
        writer.writerow(data)

def create_pack_virus(nome_csv):
    data = ['Date','Architecture','Hash','Filename','Result']
    with open(nome_csv,"w") as r:
        writer = csv.writer(r)
        writer.writerow(data)

def add_row(nome_csv,data):
    with open(nome_csv,mode="a") as r:
        writer = csv.writer(r, quoting=csv.QUOTE_NONE, escapechar='\\')
        writer.writerow(data)

def update_csv(nome_csv):
    last_row = get_last_row("report.csv")
    add_row(eset_csv,last_row)




def check_virus(virus):
    sleep(1)
    #controlla se il virus è passato
    get_url = os.path.join("http://192.168.56.101:8080/virus",virus)
    curl_command = ["VBoxManage", "guestcontrol", analyzer, "run", curl, "--username", username_analyzer, "--password", password_analyzer, "--wait-stdout","--",get_url]
    result = subprocess.run(curl_command,stdout = subprocess.PIPE,universal_newlines = True)
    return result.stdout




def exe_inside_sandbox(virus,packer):
    #rendi il file eseguibile
    print("cambia permessi su: "+virus)
    chmod_command =f"VBoxManage guestcontrol {sandbox} run {chmod} --username {username_sandbox} --password {password_sandbox} --wait-stdout -- +x {dir_virus_on_server}/{virus}" 
    os.system(chmod_command)
    
    #esegui effettivamente virus
    print("esegui virus: "+virus)
    exe_cmd = f"{dir_virus_on_server}/{virus}"
    exe_command = ["VBoxManage", "guestcontrol", sandbox, "run", exe_cmd, "--username", username_sandbox, "--password", password_sandbox, "--wait-stdout"]
    try:
        # Imposta un gestore di timeout per 2 minuti
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(120)  # 120 secondi (2 minuti)
        # Esegui il comando e cattura l'output
        result = subprocess.run(exe_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
        if packer:
            data = [datetime.now(), get_bit(virus), get_sha1(virus), virus,result.stdout.strip()]
        else:
            data = [datetime.now(), get_sha1(virus).strip(), " ", result.stdout.strip()]
        # Disattiva il timer di timeout
        signal.alarm(0)
    except subprocess.CalledProcessError as e:
        # Se il comando restituisce un codice di ritorno diverso da zero (34), gestisci l'errore
        if packer:
            data = [datetime.now(), " ", " ", " ",e.stderr.strip()]
        else: 
            data = [datetime.now(), get_sha1(virus).strip(), virus,e.stderr.strip()]
    except TimeoutError:
        # Se il timeout viene raggiunto, restituisci "TIME EXCEEDED"
        if packer:
            data = [datetime.now(), " ", " ", " ", "TIME EXCEEDED"]
        else:
            data = [datetime.now(), get_sha1(virus).strip(), virus, "TIME EXCEEDED"]
    finally:
        # Disattiva il timer di timeout anche in caso di altre eccezioni
        signal.alarm(0)
    return data



def exe(virus):
    #controlla se il virus è passato
    
    if check_virus(virus) == "Il file esiste":
        data = exe_inside_sandbox(virus,False)
        #aggiungi in un report a parte
        if "passed_virus_report.csv" not in os.listdir(working_dir):
            create_csv_virus("passed_virus_report.csv")
        add_row("passed_virus_report.csv",data)
    else:
        #crea file report
        if eset_csv not in os.listdir(working_dir):
            create_eset_csv(eset_csv)
        get_report()
        update_csv(eset_csv)
    

def pack(virus):
    print("MODALITÀ PACKER")
    virus_path = os.path.join(dir_virus,virus)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(ip_analyzer, porta_analyzer, username_analyzer, password_analyzer)
        #pack.py packa il virus e lo invia insieme al loader
        _,out,_ = ssh.exec_command(f"/home/kali/Downloads/simplepack-master/pack.py {virus_path}")
        stdout = out.read().decode("utf-8")
        print(stdout)
    except Exception as e:
        print(f"Errore nella connessione SSH: {str(e)}")
    finally:
        # Chiudi la connessione SSH quando hai finito
        ssh.close()

    #controlla se il virus è passato
    if check_virus(virus) == "Il file esiste":
        #esegui virus
        data = exe_inside_sandbox("loader",True)
        data[1] = get_bit(virus)
        data[2] = get_sha1(virus)
        data[3] = virus
        #aggiungi in un report a parte
        if "pack_report.csv" not in os.listdir(working_dir):
            create_pack_virus("pack_report.csv")
        add_row("pack_report.csv",data)
    else:
        get_report()
        update_csv(eset_csv)


#  inizio
def main(packer,headless):
    #inserisci in un array tutti i file della dir dei virus
    ls_command = ["VBoxManage", "guestcontrol", analyzer, "run", ls, "--username", username_analyzer, "--password", password_analyzer, "--wait-stdout","--",dir_virus]
    result = subprocess.run(ls_command,stdout = subprocess.PIPE,universal_newlines = True)
    output = result.stdout
    file_in_dir = [line for line in output.splitlines()]

    for file in file_in_dir:
        #ripristina snap
        ripristina_snap_eset(vm,headless)
        virus_path = os.path.join(dir_virus,file)
        if packer:
            pack(file)
        else :
            #invio virus
            curl_command =f"VBoxManage guestcontrol {analyzer} run {curl} --username {username_analyzer} --password {password_analyzer} --wait-stdout -- -X POST -F \"file=@{virus_path}\" {url}" 
            os.system(curl_command)
            #esegui virus
            exe(file)
    ripristina_snap_eset(vm,headless)


if __name__ == '__main__':
    # Creare un oggetto parser
    parser = argparse.ArgumentParser()

    # Aggiungere l'argomento "--packer" e "--headless"
    parser.add_argument('--packer', action='store_true', help='invia virus al server packato')
    parser.add_argument('--headless', action='store_true', help='lancia lo script senza interfaccia')

    # Parsare gli argomenti dalla linea di comando
    args = parser.parse_args()
    
    main(args.packer,args.headless)
