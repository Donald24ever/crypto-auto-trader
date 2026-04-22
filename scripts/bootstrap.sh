#!/usr/bin/env bash
# Creates a fresh .env with random SECRET_KEY + FERNET_KEY for local dev.
set -euo pipefail

cd "$(dirname "$0")/../backend"

if [[ -f .env ]]; then
  echo ".env already exists — delete it first if you want to regenerate."
  exit 0
fi

SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
FERNET_KEY="$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"

cat > .env <<EOF
SECRET_KEY=${SECRET_KEY}
FERNET_KEY=${FERNET_KEY}
DATABASE_URL=sqlite:///./auto_trader.db
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://localhost:3000
SCHEDULER_ENABLED=true
EOF

echo "Wrote backend/.env"
