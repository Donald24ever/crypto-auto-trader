from __future__ import annotations

import os

# Deterministic keys for tests
os.environ.setdefault("SECRET_KEY", "test-secret-0123456789")
os.environ.setdefault("FERNET_KEY", "zH8s4zT4H2n1yQf8rY7aZa3L1m8Dq1wV3x2c6kP9aQI=")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SCHEDULER_ENABLED", "false")
