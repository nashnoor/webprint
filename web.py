import os
import sys
from flask import Flask, request, render_template, redirect, url_for
import cups
import tempfile

app = Flask(__name__)

@app.route('/')
def index():
     return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
    else:
        conn = cups.Connection()
        upload = request.files['upload']
        with tempfile.NamedTemporaryFile() as fp:
            upload.save(fp.name)
            conn.printFile(app.config['printer_name'], fp.name, 'WebPrinter', {})
        return redirect(url_for('upload', message="File printed successfully"))

if __name__ == '__main__':
    args = sys.argv
    port = int(args[1])
    printer_name = args[2]
    app.config['printer_name'] = printer_name
    app.run(host='0.0.0.0', port=port)

