#!/usr/bin/env bash
# Atlas Mobile MVP - SQLite 每日备份脚本
# 部署：复制到 /opt/atlas/backup_sqlite.sh
# 配置 cron：0 3 * * * /opt/atlas/backup_sqlite.sh >> /var/log/atlas_backup.log 2>&1

set -euo pipefail

# 数据库目录（与 .env 的 DATABASE_PATH 一致）
DB_DIR="${DATABASE_PATH:-/opt/atlas/data}"
BACKUP_DIR="${BACKUP_DIR:-/opt/atlas/backups}"
KEEP_DAYS="${KEEP_DAYS:-14}"

mkdir -p "$BACKUP_DIR"

# 备份（带日期）
STAMP=$(date +%F)
cp "$DB_DIR/mobile_mvp.db" "$BACKUP_DIR/mobile_mvp_${STAMP}.db"

# 清理过期备份（保留 N 天）
find "$BACKUP_DIR" -name "mobile_mvp_*.db" -mtime +"$KEEP_DAYS" -delete

echo "[$(date '+%F %T')] backup done: $BACKUP_DIR/mobile_mvp_${STAMP}.db"
