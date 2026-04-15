#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/srv/blog"
VENV_PATH="$APP_DIR/.venv"
PYTHON_BIN="$VENV_PATH/bin/python"
PIP_BIN="$VENV_PATH/bin/pip"

cd "$APP_DIR"

git fetch --all
git reset --hard origin/main

if [ ! -d "$VENV_PATH" ]; then
  python3 -m venv "$VENV_PATH"
fi

"$PIP_BIN" install --upgrade pip
"$PIP_BIN" install -r requirements.txt

"$PYTHON_BIN" manage.py migrate --noinput
"$PYTHON_BIN" manage.py collectstatic --noinput
"$PYTHON_BIN" manage.py check --deploy

sudo systemctl restart blog
sudo systemctl reload nginx

echo "Deploy complete."
