#!/usr/bin/env bash

if [ $MODE = "export" ]; then
  /app/scripts/export.sh
elif [ $MODE = "import" ]
then
  /app/scripts/import.sh
else
  echo "Unknown mode"
fi
