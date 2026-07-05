"""Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb"""

import tempfile
import os
from core.storage import SQLiteStorage


def test_sqlite_storage_basic():
    d = tempfile.TemporaryDirectory()
    dbpath = os.path.join(d.name, 'bots.db')
    s = SQLiteStorage(dbpath)
    s.add_admin(12345)
    assert 12345 in s.get_admins()
    s.add_premium_user(111, 'silver')
    assert s.is_premium(111)
    s.remove_premium_user(111)
    assert not s.is_premium(111)
