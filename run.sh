#!/usr/bin/env bash
# WebClone v2.0 Linux Başlatıcı
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

if command -v python3 >/dev/null 2>&1; then
    exec python3 gui.py "$@"
elif command -v python >/dev/null 2>&1; then
    exec python gui.py "$@"
else
    echo "Hata: Python 3 bulunamadı! Lütfen Python 3 kurun."
    exit 1
fi
