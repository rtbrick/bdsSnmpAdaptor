#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio

import aiohttp

DUT_REST_IP = "127.0.0.1"
DUT_REST_PORT = 5000


async def sendRequests():
    httpRequestCounter = 0

    url = "http://{}:{}/dummyUrl".format(DUT_REST_IP, DUT_REST_PORT)
    headers = {'Content-Type': 'application/json'}

    async with aiohttp.ClientSession() as session:

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

            # print (testJsonDict)
            # async with session.post(url, json={'test': 'object'})

            async with session.post(url, headers=headers, json=testJsonDict) as resp:
                await resp.json()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    loop.run_until_complete(
        sendRequests())

    loop.close()
