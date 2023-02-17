#!/usr/bin/env python3

"""
https://roytuts.com/python-flask-rest-api-file-upload/
"""
import os
from subprocess import PIPE, Popen
import time

from flask import Flask, request, redirect, jsonify
from flask_apscheduler import APScheduler

from utils import load_logger, load_config

fish_config = load_config()

path_to_logs = os.path.join(os.path.dirname(__file__), "api_history.log")
logger = load_logger(filename=path_to_logs)

UPLOAD_FOLDER = os.path.dirname(__file__)
ALLOWED_EXTENSIONS = set(fish_config["allowed_extention"])
PATH_TO_TMP_MESSAGE = os.path.join(os.path.dirname(__file__), "tmp_message.log")
TD_MAX = fish_config["app_max_time_between_sendings"]

app = Flask(__name__)
app.secret_key = 'kusty_sireni'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = fish_config["app_max_content_lenght"]  # bytes

# initialize scheduler
scheduler = APScheduler()
scheduler.init_app(app)

last_time = time.time()


def get_timedelta_from_last_sending():
    """ return timedelta in minuts """
    td = time.time() - last_time
    td /= 60  # to minutes
    return td


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def send_messages(path=None, msg=None):
	if isinstance(path, str) and os.path.isfile(path):
		p1 = Popen(['cat', path], stdout=PIPE)
	elif isinstance(msg, str):
		p1 = Popen(['echo', msg], stdout=PIPE)
	p2 = Popen([fish_config["app_python_cmd"], 'bot.py'], stdin=p1.stdout, stdout=PIPE)  # python3.8 explicitly
	p2.communicate()


@app.route('/fish/file-upload', methods=['POST'])
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

    global last_time
    last_time = time.time()
    return resp


@scheduler.task('interval', id='check-processing', minutes=TD_MAX - 1)
def job1():
    td = get_timedelta_from_last_sending()
    if td > TD_MAX:
        send_messages(msg="ERROR: fish-factory don't send messages; last message was received {:.2f} min ago".format(td))
        logger.warning("Time from last sending: {:.2f} min".format(td))
    else:
        logger.info("Time from last sending: {:.2f} min".format(td))


scheduler.start()

if __name__ == '__main__':
	app.run(host=fish_config["app_ip"], port=fish_config["app_port"])
