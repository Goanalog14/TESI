import subprocess
import os
import signal
from time import sleep
from datetime import datetime
import virtualbox
import csv
import paramiko


vbox = virtualbox.VirtualBox()
#dir_virus="/home/kali/Virus/set_virus"
dir_virus="/home/kali/Virus/exe_virus2"
dir_virus_on_server="/home/user/virus_test_eset/flask_server/virus"
url = "http://192.168.56.101:8080/uploader"
kali = "kali-linux"
username = "kali"
password = "kali"
eset = "eset"
eset_snap = "flask3_ssh"
my_csv = "my_report.csv"
vm = vbox.find_machine(eset)



def get_report():
    command_generate_report = f"VBoxManage guestcontrol {kali} run /home/kali/Virus_test_eset/get_report.py --username {username} --password {password} --wait-stdout"
    os.system(command_generate_report)
    
    ip = "192.168.56.103"
    porta = 22
    remote_file_path = "/home/kali/Virus_test_eset/report.csv"
    local_file_path = "/home/simone/Scrivania/Script/report.csv"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(ip, porta, username, password)
        sftp = ssh.open_sftp()
        sftp.get(remote_file_path,local_file_path)
        print(f"File copiato con successo da {remote_file_path} a {local_file_path}")
    except Exception as e:
        print(f"Errore nella connessione SSH: {str(e)}")
    finally:
            # Chiudi la connessione SSH quando hai finito
        sftp.close()
        ssh.close()

def ripristina_snap_eset(vm):
    if vm.state != 0:
        subprocess.call(['VBoxManage','controlvm',eset,'poweroff'])
        sleep(4)
    subprocess.call([f'VBoxManage', 'snapshot', "eset", 'restore', eset_snap])
    subprocess.call(['VBoxManage', 'startvm', "eset"])

def get_sha1(virus):
    virus_path = os.path.join(dir_virus,virus)
    print(virus_path)
    sha1_command = [f"VBoxManage", "guestcontrol", kali, "run", "/home/kali/Virus_test_eset/sha1.py", "--username", username, "--password", password, "--wait-stdout","--",virus_path]
    result = subprocess.run(sha1_command,stdout = subprocess.PIPE,universal_newlines = True)
    digest = result.stdout
    return digest
    
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

def create_csv(nome_csv):
    data = ['Time detected', 'Severity', 'Scanner', 'Object URI', 'Detection', 'Detection Type', 'Action', 'User', 'Application', 'Circumstances', 'Hash', 'Raw detection name']
    with open(nome_csv,"w") as r:
        writer = csv.writer(r)
        writer.writerow(data)

def create_csv_virus(nome_csv):
    data = ['Date','Hash','Filename','Result']
    with open(nome_csv,"w") as r:
        writer = csv.writer(r)
        writer.writerow(data)

def add_row(nome_csv,data):
    with open(nome_csv,mode="a") as r:
        writer = csv.writer(r, quoting=csv.QUOTE_NONE, escapechar='\\')
        writer.writerow(data)

def update_csv(nome_csv):
    last_row = get_last_row("report.csv")
    add_row(my_csv,last_row)

# RIPRENDI DA QUI!! FUNZIONE DA CONTROLLARE 
def exe(virus):
    #controlla se il virus è passato
    curl = "/usr/bin/curl"
    get_url = os.path.join("http://192.168.56.101:8080/virus",virus)
    curl_command = ["VBoxManage", "guestcontrol", kali, "run", curl, "--username", username, "--password", password, "--wait-stdout","--",get_url]
    result = subprocess.run(curl_command,stdout = subprocess.PIPE,universal_newlines = True)
    output = result.stdout
    if output == "Il file esiste":
        #rendi il file eseguibile
        print("cambia permessi su: "+virus)
        chmod_cmd = "/usr/bin/chmod"
        chmod_command =f"VBoxManage guestcontrol {eset} run {chmod_cmd} --username user --password password --wait-stdout -- +x {dir_virus_on_server}/{virus}" 
        os.system(chmod_command)
        #esegui effettivamente virus
        print("esegui virus: "+virus)
        exe_cmd = f"{dir_virus_on_server}/{virus}"
        exe_command = ["VBoxManage", "guestcontrol", eset, "run", exe_cmd, "--username", "user", "--password", "password", "--wait-stdout"]
        try:
            # Imposta un gestore di timeout per 2 minuti
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(120)  # 120 secondi (2 minuti)
            # Esegui il comando e cattura l'output
            result = subprocess.run(exe_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
            data = [datetime.now(),get_sha1(virus).strip(),virus,result.stdout.strip()]
            # Disattiva il timer di timeout
            signal.alarm(0)
        except subprocess.CalledProcessError as e:
            # Se il comando restituisce un codice di ritorno diverso da zero (34), gestisci l'errore
            data = [datetime.now(),get_sha1(virus).strip(),virus,e.stderr.strip()]
        except TimeoutError:
            # Se il timeout viene raggiunto, restituisci "TIME EXCEEDED"
            data = [datetime.now(), get_sha1(virus).strip(), virus, "TIME EXCEEDED"]
        finally:
            # Disattiva il timer di timeout anche in caso di altre eccezioni
            signal.alarm(0)
        #aggiungi in un report a parte
        if "report_virus.csv" not in os.listdir("/home/simone/Scrivania/Script"):
            create_csv_virus("report_virus.csv")
        add_row("report_virus.csv",data)
    else:
        print("cose strane accadono")
        get_report()
        update_csv(my_csv)
    

#  inizio

#inserisci in un array tutti i file della dir dei virus
ls = "/usr/bin/ls"
ls_command = ["VBoxManage", "guestcontrol", kali, "run", ls, "--username", username, "--password", password, "--wait-stdout","--",dir_virus]
result = subprocess.run(ls_command,stdout = subprocess.PIPE,universal_newlines = True)
output = result.stdout
file_in_dir = [line for line in output.splitlines()]

#crea file report
if my_csv not in os.listdir("/home/simone/Scrivania/Script"):
    create_csv(my_csv)

for file in file_in_dir:
    #restore snap
    ripristina_snap_eset(vm)
    virus_path = os.path.join(dir_virus,file)
    #invio virus
    curl='/usr/bin/curl'
    command =f"VBoxManage guestcontrol kali-linux run {curl} --username {username} --password {password} --wait-stdout -- -X POST -F \"file=@{virus_path}\" {url}" 
    os.system(command)
    #esegui virus
    exe(file)
    #ricevi report
    #get_report()
    #manipola csv
    #update_csv(my_csv)
#restore snap
ripristina_snap_eset(vm)