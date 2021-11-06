#!/bin/bash

set -euo pipefail

curl -X 'POST' \
  'http://localhost:5000/hook_slinger/' \
  -H 'accept: application/json' \
  -H 'Authorization: Token $5$1O/inyTZhNvFt.GW$Zfckz9OL.lm2wh3IewTm8YJ914wjz5txFnXG5XW.wb4' \
  -H 'Content-Type: application/json' \
  -d '{
  "to_url": "https://webhook.site/37ad9530-59c3-430d-9db6-e68317321a9f",
  "to_auth": "",
  "tag": "Dhaka",
  "group": "Bangladesh",
  "payload": {
    "greetings": "Hello, world!"
  }
}' | python -m json.tool
