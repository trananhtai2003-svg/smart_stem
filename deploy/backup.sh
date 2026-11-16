#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p backups
STAMP=$(date +%Y%m%d_%H%M%S)
# SQLite online backup API avoids copying a live DB mid-write.
docker compose exec -T smartstem python - <<'PY' > "backups/db_${STAMP}.sqlite"
import sqlite3, sys
src=sqlite3.connect('/app/data/smart_stem.db')
dst=sqlite3.connect('/tmp/backup.sqlite')
src.backup(dst)
dst.close(); src.close()
with open('/tmp/backup.sqlite','rb') as f: sys.stdout.buffer.write(f.read())
PY
tar -czf "backups/storage_${STAMP}.tar.gz" storage
find backups -type f -mtime +14 -delete
echo "Da tao backup: backups/db_${STAMP}.sqlite va storage_${STAMP}.tar.gz"
