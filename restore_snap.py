import virtualbox


vbox = virtualbox.VirtualBox()
session=virtualbox.Session()
name="restore_snap"

try:
    vm = vbox.find_machine("kali-linux")
    snap = vm.find_snapshot("kali_post_prova")
    vm.create_session(session=session)
    snap = vm.restore_snapshot()
except Exception as e:
        print(f"EXCEPTION {name} {str(e)}")

restoring = session.machine.restore_snapshot(snap)



session.unlock_machine()
if restoring.completed == 1:
    print("restore complete")
else:
    print("restore failed")