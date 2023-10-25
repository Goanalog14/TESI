#Example: how to use VBoxMange guestcontrol
import subprocess
import virtualbox

nome_vm = "kali-linux"
username = "kali"
password = "kali"
command="/usr/bin/date"
vbox_command = ["VBoxManage","guestcontrol",nome_vm,"run",command,"--username",username,"--password",password,"--wait-stdout",]

subprocess.run(vbox_command)
