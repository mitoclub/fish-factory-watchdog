import os
from subprocess import Popen
import tempfile

import requests

URL_SEND_MESSAGES = os.environ.get("FISH_PROXY_SERVER")
_, TMP_FILE = tempfile.mkstemp(".log", "fish_")


def main():
    with open(TMP_FILE, "w") as fout:
        p = Popen(['echo', 'test message'], stdout=fout)
        p.communicate()

    with open(TMP_FILE, "rb") as fin:
        files = {'file': fin}
        try:
            r = requests.post(URL_SEND_MESSAGES, files=files)
            print(r)
        except Exception as e:
            print("ERROR: Cannot send message: " + repr(e))


if __name__ == "__main__":
    main()
