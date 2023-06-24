#!/bin/bash

function generate_html {
    echo "Running generate_html.py..."
    python3 -m generate_html

    if [ $? -eq 0 ]; then
        echo "generate_html.py completed successfully."
    else
        echo "generate_html.py encountered an error." >&2
        exit 1
    fi
}

# Initial generation
generate_html

# Start watcher
if [[ $1 == "dev" ]]; then
    echo "Starting local server..."
    (
        cd generated
        python3 -m http.server 8000 &
    )
    echo "Watching markdown files for changes..."
    watchmedo shell-command \
        --patterns="*.md" \
        --recursive \
        --command='bash -c "./build.sh"' \
        .
fi
