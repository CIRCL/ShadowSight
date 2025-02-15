#!/usr/bin/env python3
"""

call-api.py : Shadowserver Foundation API Utility

This script requires your API details to be stored in ~/.shadowserver.api
with the following contents:

--
[api]
key = 123456798
secret = MySecret
uri = https://transform.shadowserver.org/api2/
--

This script may be called with two or three arguments:

    call-api.py <method> <request> [pretty|binary]

The request must be a valid JSON object.

Simple usage:

$ ./call-api.py test/ping '{}'
{"pong":"2020-10-26 23:06:37"}

Pretty output:

$ ./call-api.py test/ping '{}' pretty
{
    "pong": "2020-10-26 23:06:42"
}

"""

import configparser
import hashlib
import hmac
import json
import os
import sys
from urllib.request import Request, urlopen

from shadowsight import config

TIMEOUT = 45


def api_call(method, request):
    """
    Call the specified api method with a request dictionary.

    """

    url = config.shadow_uri + method

    request["apikey"] = config.shadow_key
    request_string = json.dumps(request)

    secret_bytes = bytes(str(config.shadow_secret), "utf-8")
    request_bytes = bytes(request_string, "utf-8")

    hmac_generator = hmac.new(secret_bytes, request_bytes, hashlib.sha256)
    hmac2 = hmac_generator.hexdigest()

    ua_request = Request(url, data=request_bytes, headers={"HMAC2": hmac2})
    response = urlopen(ua_request, timeout=TIMEOUT)

    return response.read()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        exit("Usage: call-api.py method json [pretty|binary]")

    try:
        api_request = json.loads(sys.argv[2])
    except Exception as e:
        exit("JSON Exception: " + format(e))

    try:
        config.shadow_key
    except configparser.NoSectionError:
        exit(
            "Exception: " + os.environ["HOME"] + "/.shadowserver.api could "
            "not be found. Exiting."
        )

    try:
        res = api_call(sys.argv[1], api_request)
    except Exception as e:
        exit("API Exception: " + format(e))

    if len(sys.argv) > 3:
        if sys.argv[3] == "pretty":
            try:
                print(json.dumps(json.loads(res), indent=4))
            except Exception:
                print(res.decode("utf-8"))
        elif sys.argv[3] == "binary":
            os.write(1, res)
        else:
            exit("Unknown option " + sys.argv[3])
    else:
        print(res.decode("utf-8"))
