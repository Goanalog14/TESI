from flask import Flask, render_template, request
import os
import datetime as dt

app = Flask(__name__)
baseFolder="/home/simone/Scrivania/hello_flask/dir"
UPLOAD_FOLDER = "/home/simone/Scrivania/hello_flask/dir"

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


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route("/virus")
def virus():
    def selectStat(x):
        fileStat = x.stat()
        file_path = os.path.join(baseFolder,x)
        fIcon = 'bi bi-folder-fill' if os.path.isdir(file_path) else 'bi bi-file-earmark-text'
        
        fileSize = getReadableByteSize(fileStat.st_size)
        fileTimestamp = getTimeStampString(fileStat.st_mtime)
        return {'name':x.name, 'bytes':fileSize, 'time':fileTimestamp,'type':fIcon}
    Files= [selectStat(x) for x in os.scandir(baseFolder)]
    return  render_template('files.html',files=Files)


@app.route("/uploader", methods=['POST'])
def post_file():
    uploaded_file = request.files['file']
    if uploaded_file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'],uploaded_file.filename)
        uploaded_file.save(file_path)
        print(uploaded_file)

        return 'File caricato con successo.'

app.run(host="0.0.0.0", port=50100, debug=True)
