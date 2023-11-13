import subprocess
import os
from time import sleep
import virtualbox
import requests
import csv
import paramiko


vbox = virtualbox.VirtualBox()
dir_virus="/home/kali/Virus/set_virus"
url = "http://192.168.56.101:8080/uploader"
kali = "kali-linux"
username = "kali"
password = "kali"
eset = "eset"
eset_snap = "flask_ssh"
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
    subprocess.call([f'VBoxManage', 'snapshot', "eset", 'restore', 'flask_ssh'])
    subprocess.call(['VBoxManage', 'startvm', "eset"])

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

def add_row(nome_csv,data):
    with open(nome_csv,mode="a") as r:
        writer = csv.writer(r)
        writer.writerow(data)

def update_csv(nome_csv):
    last_row = get_last_row("report.csv")
    add_row(my_csv,last_row)



#inserisci in un array tutti i file nella dir dei virus
ls = "/usr/bin/ls"
ls_command = ["VBoxManage", "guestcontrol", kali, "run", ls, "--username", username, "--password", password, "--wait-stdout","--",dir_virus]
result = subprocess.run(ls_command,stdout = subprocess.PIPE,universal_newlines = True)
output = result.stdout
file_in_dir = [line for line in output.splitlines()]

#crea file report
#create_csv(my_csv)



for file in file_in_dir:
    #restore snap
    ripristina_snap_eset(vm)
    virus_path = os.path.join(dir_virus,file)
    #invio virus
    curl='/usr/bin/curl'
    command =f"VBoxManage guestcontrol kali-linux run {curl} --username {username} --password {password} --wait-stdout -- -X POST -F \"file=@{virus_path}\" {url}" 
    os.system(command)
    #esegui virus
    print("esegui virus")
    #ricevi report
    get_report()
    #manipola csv
    update_csv(my_csv)
    #restore snap
ripristina_snap_eset(vm)