import sqlite3
import tempfile
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from app.dbfile import carry_over_old_database


def make_db(path, value):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE t (v TEXT)")
    con.execute("INSERT INTO t VALUES (?)", (value,))
    con.commit()
    con.close()


def read_db(path):
    con = sqlite3.connect(path)
    try:
        return con.execute("SELECT v FROM t").fetchone()[0]
    finally:
        con.close()


class DatabaseFileLocationTests(SimpleTestCase):
    """Baza faylı apps/-dan bir qovluq yuxarıdadır; köhnə baza itmədən köçürülür."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.old = self.dir / "apps" / "db.sqlite3"
        self.old.parent.mkdir()
        self.new = self.dir / "db.sqlite3"

    def test_db_file_is_one_folder_above_manage_py(self):
        self.assertEqual(settings.DB_FILE, settings.BASE_DIR.parent / "db.sqlite3")
        self.assertTrue((settings.BASE_DIR / "manage.py").exists())

    def test_old_database_is_copied_when_new_is_missing(self):
        make_db(self.old, "canlı məlumat")
        self.assertTrue(carry_over_old_database(self.old, self.new))
        self.assertEqual(read_db(self.new), "canlı məlumat")
        # köhnə fayl ehtiyat kimi yerində qalır, müvəqqəti fayl qalmır
        self.assertEqual(read_db(self.old), "canlı məlumat")
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), ["apps", "db.sqlite3"])

    def test_existing_new_database_is_never_overwritten(self):
        make_db(self.old, "köhnə")
        make_db(self.new, "yeni")
        self.assertFalse(carry_over_old_database(self.old, self.new))
        self.assertEqual(read_db(self.new), "yeni")

    def test_nothing_happens_without_old_database(self):
        self.assertFalse(carry_over_old_database(self.old, self.new))
        self.assertFalse(self.new.exists())
