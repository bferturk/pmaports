#!/usr/bin/env python3
import argparse
import json
import os
import requests

# Require environment vars
for key in ["BPO_API_ENDPOINT",
            "BPO_API_HOST",
            "BPO_ARCH",
            "BPO_TOKEN_FILE",
            "BPO_PAYLOAD_FILES",    # space separated list of files
            "BPO_PAYLOAD_IS_JSON",  # set to "1" to enable
            "BPO_PUSH_ID",
            ]:
    if not key in os.environ:
        print("ERROR: missing environment variable: " + key)
        exit(1)

# Parse and check files
files = os.environ["BPO_PAYLOAD_FILES"].split(" ")
for path in files:
    if not os.path.exists(path):
        print("ERROR: file not found: " + path)
        exit(1)

# Load token
with open(os.path.expanduser(os.environ["BPO_TOKEN_FILE"]),
          encoding="utf-8") as handle:
    token = handle.read().strip()

# Load other env vars
url = (os.environ["BPO_API_HOST"] + "/api/job-callback/" +
       os.environ["BPO_API_ENDPOINT"])
arch = os.environ["BPO_ARCH"]
is_json = (os.environ["BPO_PAYLOAD_IS_JSON"] == "1")
push_id = os.environ["BPO_PUSH_ID"]

# Submit JSON
if is_json:
    if len(files) > 1:
        print("ERROR: json mode doesn't support multiple input files")
        exit(1)

    # Send contents of file as HTTP POST with json payload
    with open(files[0], encoding="utf-8") as handle:
        data = handle.read()
    data = json.loads(data)

    print("Sending JSON to: " + url)
    response = requests.post(url, json=data, headers={
        "X-BPO-Arch": arch,
        "X-BPO-Push-Id": push_id,
        "X-BPO-Token": token,
    })
else:  # Submit blobs
    for path in files:
        filename = os.path.basename(path)
        # Send contents of file as HTTP POST with multipart/formdata payload
        print("Appending: " + path)
        files.append(("file[]", (filename,
                                 open(path, "rb"),
                                 "application/octet-stream")))

    print("Uploading to: " +  url)

    response = requests.post(url, files=files, headers={
        "X-BPO-Arch": arch,
        "X-BPO-Push-Id": push_id,
        "X-BPO-Token": token,
    })

if response.status_code > 399:
    print("Error occurred:")
    print(response.content.decode())
    exit(1)
else:
    print(response.content.decode())
