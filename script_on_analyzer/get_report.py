#!/usr/bin/python3

import paramiko 

ip = "192.168.56.101"
porta = 22
username = "root"
password = "password"
remote_file_path = "/opt/eset/eea/sbin/report.csv"
local_file_path = "/home/kali/Virus_test_eset/report.csv"
print("forse siamo sulla buona strada")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(ip, porta, username, password)
    print("connessione riuscitaaa :'D")
    stdin, stdout, stderr = ssh.exec_command("cd /opt/eset/eea/sbin ; ./lslog -d -c > report.csv")
    print("Risultato del comando :")
    print(stdout.read().decode())
    sftp = ssh.open_sftp()
    sftp.get(remote_file_path,local_file_path)
    print(f"File copiato con successo da {remote_file_path} a {local_file_path}")
except Exception as e:
    print(f"Errore nella connessione SSH: {str(e)}")

finally:
        # Chiudi la connessione SSH quando hai finito
    sftp.close()
    ssh.close()
