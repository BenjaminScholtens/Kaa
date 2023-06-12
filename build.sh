#!/bin/bash

echo "Running generate_html.py..."

python3 -m generate_html

if [ $? -eq 0 ]; then
    echo "generate_html.py completed successfully."
else
    echo "generate_html.py encountered an error." >&2
fi
