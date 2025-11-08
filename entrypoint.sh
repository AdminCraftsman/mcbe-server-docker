#!/bin/bash
# entrypoint.sh

# If argument is "bash" or "shell", start interactive shell
if [ "$1" = "bash" ] || [ "$1" = "shell" ]; then
  exec /bin/bash
fi

# Start the server
exec ./bedrock_server