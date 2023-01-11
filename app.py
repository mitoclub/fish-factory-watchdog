#!/usr/bin/env python3

"""
https://roytuts.com/python-flask-rest-api-file-upload/
"""
import os
from subprocess import PIPE, Popen
from flask import Flask, request, redirect, jsonify

UPLOAD_FOLDER = os.path.dirname(__file__)
ALLOWED_EXTENSIONS = set(['txt', 'log'])
PATH_TO_TMP_MESSAGE = os.path.join(os.path.dirname(__file__), "tmp_message.log")

app = Flask(__name__)
app.secret_key = 'kusty_sireni'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100_000  # bytes

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def send_messages(path=None, msg=None):
	if isinstance(path, str) and os.path.isfile(path):
		p1 = Popen(['cat', path], stdout=PIPE)
	elif isinstance(msg, str):
		p1 = Popen(['echo', msg], stdout=PIPE)
	p2 = Popen(['python3.8', 'bot.py'], stdin=p1.stdout, stdout=PIPE)  # python3.8 explicitly
	p2.communicate()


@app.route('/file-upload', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
    else:
        file = request.files['file']
        if file.filename == '':
            resp = jsonify({'message' : 'No file selected for uploading'})
            resp.status_code = 400
        elif file and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], PATH_TO_TMP_MESSAGE))
            resp = jsonify({'message' : 'File successfully uploaded'})
            resp.status_code = 201
        else:
            resp = jsonify({'message' : 'Allowed file types are txt, log'})
            resp.status_code = 400
    
    if resp.status_code == 400:
        send_messages(msg="ERROR: Recieved bad file")
    elif resp.status_code == 201:
        send_messages(path=PATH_TO_TMP_MESSAGE)
    else:
        print(repr(resp))
        send_messages(msg="ERROR: Cannot receive file, status code {}".format(resp.status_code))

    return resp


if __name__ == '__main__':
	app.run()
