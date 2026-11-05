"""Baza faylının yeri dəyişəndə köhnə bazanı yeni yerə köçürən köməkçi."""
import os
import sqlite3
import sys
from pathlib import Path


def carry_over_old_database(old_path, new_path):
    """Yeni yerdə baza yoxdursa, köhnə yerdəki bazanın surətini ora yazır.

    - Yeni yerdə fayl artıq varsa heç nə etmir (heç vaxt üstünə yazmır).
    - Köhnə fayl silinmir, ehtiyat kimi yerində qalır.
    - Surət SQLite-ın öz "backup" üsulu ilə çıxarılır: köhnə baza həmin an
      istifadədə olsa belə surət bütöv alınır.

    Köçürmə olubsa True, olmayıbsa False qaytarır.
    """
    old_path, new_path = Path(old_path), Path(new_path)
    if new_path.exists() or not old_path.exists():
        return False

    tmp_path = new_path.with_name(f"{new_path.name}.{os.getpid()}.tmp")
    tmp_path.unlink(missing_ok=True)
    source = sqlite3.connect(old_path)
    try:
        target = sqlite3.connect(tmp_path)
        try:
            source.backup(target)
        finally:
            target.close()
    finally:
        source.close()

    try:
        # os.link mövcud faylın üstünə yazmır: eyni anda başqa proses köçürübsə
        # onun faylı qalır, bizimki atılır.
        os.link(tmp_path, new_path)
    except FileExistsError:
        return False
    finally:
        tmp_path.unlink(missing_ok=True)

    print(f"[baza] Köhnə baza yeni yerə köçürüldü: {old_path} -> {new_path}", file=sys.stderr)
    return True
