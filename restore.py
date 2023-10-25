#Example : how to restore a snapshot
import subprocess
import virtualbox

vbox = virtualbox.VirtualBox()
vm_name = "kali-linux"

vm = vbox.find_machine(vm_name)


# Controlla che la vm è spenta
if vm.state != 1:
    print("non è spenta")
    # allora spengi
    subprocess.call(['VBoxManage','controlvm',vm_name,'poweroff'])
else:
    print("è spenta")

# restore snap and restart machine
subprocess.call(['VBoxManage', 'snapshot', vm_name, 'restore', "vm_post_prova"])
subprocess.call(['VBoxManage', 'startvm', vm_name])

