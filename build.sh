#!/bin/bash

echo "Running generate_html.py..."

python3 -m generate_html

if [ $? -eq 0 ]; then
    echo "generate_html.py completed successfully."
else
    echo "generate_html.py encountered an error." >&2
    exit 1
fi

if [[ $1 == "dev" ]]; then
    echo "Starting local server..."
    (
        cd generated
        python3 -m http.server 8000
    )
fi
