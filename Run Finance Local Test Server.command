#!/bin/bash
set -euo pipefail

APP_DIR="/Users/ronholl/Documents/Apps/Ron_Finance_Model/Deployed Versions/Version 1.5"
PORT="8081"
CACHE_BUST="$(date +%s)"
URL="http://localhost:${PORT}/index.html?previewMessage=1&check=${CACHE_BUST}"

clear
echo "Starting Ron's Retirement Finance Model local test server..."
echo
echo "Serving folder:"
echo "  ${APP_DIR}"
echo
echo "Open this URL to force-preview user-message.json:"
echo "  ${URL}"
echo
echo "For normal local testing without forcing the message, use:"
echo "  http://localhost:${PORT}/index.html?check=${CACHE_BUST}"
echo
echo "Press Control-C in this window to stop the server."
echo
cd "${APP_DIR}"
python3 -m http.server "${PORT}" --bind 127.0.0.1
