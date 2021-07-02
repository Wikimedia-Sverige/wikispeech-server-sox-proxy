#!/usr/bin/env bash

echo "Starting Wikispeech server SOX proxy."
python3 sox-proxy.py &
PID=$!
sleep 10
if ! kill -0 ${PID}; then
  echo "ERROR: Service has prematurely ended!"
  exit 1
fi
wget -O /dev/null -o /dev/null "http://localhost:5000/ping"
EXIT_CODE=$?
kill ${PID}
if [ ${EXIT_CODE} -ne 0 ]; then
  echo "ERROR: Test failed!"
else
  echo "Test successful!"
fi
exit ${EXIT_CODE}
