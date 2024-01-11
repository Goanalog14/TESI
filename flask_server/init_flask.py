from flask import Flask, render_template, request, make_response
import os
import datetime as dt
import socket
import fcntl
import struct

app = Flask(__name__)
UPLOAD_FOLDER = "/home/user/virus_test_eset/flask_server/virus"

@app.route("/")
def homepage():
    return "Hello World!!"

def getReadableByteSize(num, suffix='B') -> str:
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def getTimeStampString(tSec: float) -> str:
    tObj = dt.datetime.fromtimestamp(tSec)
    tStr = dt.datetime.strftime(tObj, '%Y-%m-%d %H:%M:%S')
    return tStr


def get_ip_address(interface_name):
    try:
        # Ottieni l'indirizzo IP associato all'interfaccia specificata
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_address = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', bytes(interface_name, 'utf-8')))[20:24])
        return ip_address
    except Exception as e:
        print(f"Errore nell'ottenere l'indirizzo IP dell'interfaccia {interface_name}: {e}")
        return None

# Specifica il nome dell'interfaccia desiderata
interface_name = 'eth0'  # Sostituisci con il nome dell'interfaccia desiderata

# Ottieni l'indirizzo IP dell'interfaccia specificata
ip_address = get_ip_address(interface_name)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route("/virus")
def virus():
    def selectStat(x):
        fileStat = x.stat()
        file_path = os.path.join(UPLOAD_FOLDER,x)
        fIcon = 'bi bi-folder-fill' if os.path.isdir(file_path) else 'bi bi-file-earmark-text'
        
        fileSize = getReadableByteSize(fileStat.st_size)
        fileTimestamp = getTimeStampString(fileStat.st_mtime)
        return {'name':x.name, 'bytes':fileSize, 'time':fileTimestamp,'type':fIcon}
    Files= [selectStat(x) for x in os.scandir(UPLOAD_FOLDER)]
    return  render_template('files.html',files=Files,ip=ip_address)

@app.route("/virus/<file_name>")
def get_virus(file_name):
    filepath = os.path.join(UPLOAD_FOLDER,file_name)
    if os.path.exists(filepath):
        return make_response("Il file esiste",200)
    else: 
        return make_response("Il file non esiste",404)

@app.route("/uploader", methods=['POST'])
def post_file():
    uploaded_file = request.files['file']
    if uploaded_file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'],uploaded_file.filename)
        uploaded_file.save(file_path)
        print(uploaded_file)

        return 'File caricato con successo.'

app.run(host="0.0.0.0", port=8080, debug=True)
