# Virus test eset
Il repository è composto principalmente di 4 directory e un programma in python chiamato **main_virus.py** che si occupa di automatizzare l'attività di testing.
Mentre per quanto riguarda le directory abbiamo:
## Script
che contiene alcuni degli script in python che ho utilizzato sia in fase di costruzione dell'infrastruttura, sia in fase di testing
## flask_server
che contiene il server flask in grado di ricevere le get e le post dei virus e che quindi racchiude tutto ciò che deve contenere la macchina sandbox per funzionare
## script_on_analyzer
che contiene gli script che da main_virus.py vengono richiamati direttamente sulla macchina analyzer ed eseguiti
## report
che contiene i report generati dall'esecuzione del programma main_virus.py
