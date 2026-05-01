#!/bin/bash
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

if [ ! -f "venv/bin/activate" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -q -r requirements.txt

echo "Starting PostgreSQL in Docker..."
docker compose up -d

echo "Waiting for PostgreSQL to be ready..."
until docker compose exec -T db pg_isready -U farmsure -d farmsure > /dev/null 2>&1; do
  sleep 1
done
echo "PostgreSQL is ready."

echo "Launching Farmer app..."
python portal.py &

echo "Launching Back-Office app..."
python backoffice.py &

echo "Both apps are running. Close this terminal to stop them."
wait
