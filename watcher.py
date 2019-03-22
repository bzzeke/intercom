#!/usr/bin/env python

import os
import json
import urllib2
import time
import util

DELAY = 2
MULTIPLIER = 2

def process(filename):

    file_path = os.environ['SNAPSHOT_PATH'] + '/' + filename
    with open(file_path, mode='rb') as file:
        content = file.read()

    req = urllib2.Request(os.environ['API_URL'])
    req.add_header('Content-Type', 'application/json')

    try:
        response = urllib2.urlopen(req, json.dumps({
            'text': 'Calling to the door',
            'attachments': [
                content.encode('base64')
            ]
        }))

        if response.getcode() == 200:
            os.remove(file_path)
            return True

    except Exception as e:
        print('Failed to notify: {}'.format(e))

    return False

if __name__ == '__main__':
    delay = DELAY
    while True:
        for root, dirs, files in os.walk(os.environ['SNAPSHOT_PATH']):
            for filename in files:
                if process(filename) == False:
                    delay = delay * MULTIPLIER
                    break
                else:
                    delay = DELAY

        time.sleep(delay)
