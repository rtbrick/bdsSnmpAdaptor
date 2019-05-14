#!/usr/bin/env python
# -*- coding: utf-8 -*-

DUT_REST_IP = "127.0.0.1"
DUT_REST_PORT = 5000

import json

import requests


if __name__ == '__main__':
    httpRequestCounter = 0

    while httpRequestCounter < 100:
        httpRequestCounter += 1

        testJsonDict = {
            "host": "confd",
            "full_message": f"full_message_text blablabla {httpRequestCounter}",
            "short_message": "short_message_text",
            "level": 3,
            "_time_stamp": f"663736345331532_{httpRequestCounter}",
            "_rtbrick_host": "Basesim",
            "_rtbrick_pod": "rtbrick-pod"
        }

        print(testJsonDict)

        url = "http://{}:{}/dummyUrl".format(DUT_REST_IP, DUT_REST_PORT)
        headers = {'Content-Type': 'application/json'}

        response = requests.post(
            url,
            data=json.dumps(testJsonDict),
            headers=headers, timeout=1)

        print(response.status_code)
