#!/bin/bash
set -e
echo "Starting bot..."
echo "PORT=$PORT"
echo "DEBUG=$DEBUG"
echo "TOKEN exists: $(test -n "$TOKEN" && echo yes || echo no)"
exec python -c "
import os, sys
port = int(os.environ.get('PORT', 5000))
from epush_bot import server
print('Flask imported, starting server on port', port)
sys.stdout.flush()
server.run(host='0.0.0.0', port=port)
"
