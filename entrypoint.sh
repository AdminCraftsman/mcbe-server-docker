#!/bin/bash
# entrypoint.sh

# If argument is "bash" or "shell", start interactive shell
if [ "$1" = "bash" ] || [ "$1" = "shell" ]; then
  exec /bin/bash
fi

echo "Fetching worlds..."
python3 /home/minecraft/fetch-world.py

# echo "Fetching mod packs..."
# python3 /home/minecraft/fetch-packs.py

# Start the server
echo "Starting Bedrock server..."
exec ./bedrock_server