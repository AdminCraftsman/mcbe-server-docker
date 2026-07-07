#!/bin/bash
set -euo pipefail

JSON_URL="https://raw.githubusercontent.com/kittizz/bedrock-server-downloads/main/bedrock-server-downloads.json"

echo "Fetching latest Bedrock server version..."
json=$(curl -fsSL "$JSON_URL")
latest_version=$(echo "$json" | jq -r '.release | keys[]' | sort -V | tail -1)
latest_url=$(echo "$json" | jq -r ".release[\"$latest_version\"].linux.url")

echo "Downloading version $latest_version from $latest_url..."
curl -fsSL \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36" \
  -H "Accept: application/octet-stream,*/*" \
  -H "Accept-Language: en-US,en;q=0.9" \
  -H "Referer: https://www.minecraft.net/en-us/download/server/bedrock" \
  "$latest_url" -o bedrock-server.zip

unzip bedrock-server.zip
rm bedrock-server.zip

echo "$latest_version" > .version
echo "Done. Server version: $latest_version"