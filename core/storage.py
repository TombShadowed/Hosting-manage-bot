# Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb

import json
import threading
from pathlib import Path
from typing import Dict, List, Optional
from config import BASE_DATA_DIR, MONGO_URI, MONGO_DB
import logging
from datetime import datetime, timedelta

logger = logging.getLogger('master.storage')
LOCK = threading.Lock()

try:
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except Exception:
    MongoClient = None
    MONGO_AVAILABLE = False


def get_storage():
    """Get the appropriate storage instance based on configuration."""
    if MONGO_AVAILABLE and MONGO_URI:
        return MongoStorage(MONGO_URI)
    try:
        return SQLiteStorage()
    except Exception:
        return FileStorage()


class FileStorage:
    def __init__(self, path: Path = BASE_DATA_DIR / 'bots.json'):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps({}))

    def load(self) -> Dict:
        with LOCK:
            return json.loads(self.path.read_text())

    def save(self, data: Dict):
        with LOCK:
            self.path.write_text(json.dumps(data, indent=2))

    def get_bot(self, name: str) -> Optional[Dict]:
        return self.load().get(name)

    def set_bot(self, name: str, meta: Dict):
        d = self.load()
        d[name] = meta
        self.save(d)

    def delete_bot(self, name: str):
        d = self.load()
        if name in d:
            del d[name]
            self.save(d)

    def get_admins(self) -> List[int]:
        return self.load().get('__admins__', [])
    
    def add_admin(self, tg_id: int):
        d = self.load()
        admins = set(d.get('__admins__', []))
        admins.add(int(tg_id))
        d['__admins__'] = sorted(list(admins))
        self.save(d)

    def del_admin(self, tg_id: int):
        d = self.load()
        admins = set(d.get('__admins__', []))
        if int(tg_id) in admins:
            admins.remove(int(tg_id))
            d['__admins__'] = sorted(list(admins))
            self.save(d)

    def get_premium_users(self) -> Dict[int, Dict]:
        data = self.load().get('__premium_data__', {})
        return {int(k): v for k, v in data.items()}

    def add_premium_user(self, tg_id: int, category: str = 'silver', expires_at: Optional[str] = None):
        d = self.load()
        premium_data = d.get('__premium_data__', {})
        premium_data[str(int(tg_id))] = {
            'category': category,
            'expires_at': expires_at,
            'added_at': datetime.now().isoformat()
        }
        d['__premium_data__'] = premium_data
        self.save(d)

    def remove_premium_user(self, tg_id: int):
        d = self.load()
        premium_data = d.get('__premium_data__', {})
        if str(int(tg_id)) in premium_data:
            del premium_data[str(int(tg_id))]
            d['__premium_data__'] = premium_data
            self.save(d)

    def get_premium_user(self, tg_id: int) -> Optional[Dict]:
        data = self.get_premium_users()
        return data.get(int(tg_id))

    def is_premium(self, tg_id: int) -> bool:
        user = self.get_premium_user(int(tg_id))
        if not user:
            return False
        expires_at = user.get('expires_at')
        if not expires_at:
            return True
        return datetime.fromisoformat(expires_at) > datetime.now()

    def get_premium_plan(self, tg_id: int) -> Optional[str]:
        """Get the premium plan type for a user."""
        user = self.get_premium_user(int(tg_id))
        if not user:
            return None
        expires_at = user.get('expires_at')
        if expires_at and datetime.fromisoformat(expires_at) <= datetime.now():
            return None
        return user.get('category')

    def admin_exists(self, tg_id: int) -> bool:
        """Check if a user is an admin."""
        return int(tg_id) in self.get_admins()

    def get_admin_only(self) -> bool:
        return self.load().get('__admin_only__', False)

    def set_admin_only(self, enabled: bool):
        d = self.load()
        d['__admin_only__'] = bool(enabled)
        self.save(d)

    def get_user_bots(self, user_id: int) -> int:
        """Count how many bots a user owns."""
        d = self.load()
        count = 0
        for key, value in d.items():
            if not key.startswith('__') and isinstance(value, dict):
                if value.get('owner_id') == user_id:
                    count += 1
        return count

    def save_redeem_code(self, code: str, plan: str, duration_days: int, user_limit: int):
        """Save a redeem code."""
        d = self.load()
        if '__redeem_codes__' not in d:
            d['__redeem_codes__'] = {}
        d['__redeem_codes__'][code] = {
            'plan': plan,
            'duration_days': duration_days,
            'user_limit': user_limit,
            'created_at': datetime.now().isoformat(),
            'used_by': []
        }
        self.save(d)

    def get_redeem_code(self, code: str) -> Optional[Dict]:
        """Get a redeem code."""
        codes = self.load().get('__redeem_codes__', {})
        return codes.get(code)

    def use_redeem_code(self, code: str, user_id: int) -> bool:
        """Mark a redeem code as used by a user. Returns True if successful."""
        d = self.load()
        codes = d.get('__redeem_codes__', {})
        if code not in codes:
            return False
        
        code_data = codes[code]
        used_by = code_data.get('used_by', [])
        
        # Check if user already used this code
        if user_id in used_by:
            return False
        
        # Check if code usage limit reached
        if len(used_by) >= code_data.get('user_limit', 1):
            return False
        
        # Add user to used_by list
        used_by.append(user_id)
        code_data['used_by'] = used_by
        d['__redeem_codes__'] = codes
        self.save(d)
        return True

    def delete_redeem_code(self, code: str):
        """Delete a redeem code."""
        d = self.load()
        codes = d.get('__redeem_codes__', {})
        if code in codes:
            del codes[code]
            d['__redeem_codes__'] = codes
            self.save(d)


class MongoStorage:
    def __init__(self, uri: str, dbname: str = MONGO_DB):
        if not MONGO_AVAILABLE:
            raise RuntimeError('pymongo not installed')
        self.client = MongoClient(uri)
        self.db = self.client[dbname]
        self.coll = self.db['bots']
        self.meta = self.db['meta']
        self.coll.create_index('name', unique=True)
        self.meta.create_index('key', unique=True)

    def load(self) -> Dict:
        out = {}
        for doc in self.coll.find({}, projection={'_id': False}):
            name = doc.get('name')
            if name:
                d = dict(doc)
                d.pop('name', None)
                out[name] = d
        return out

    def save(self, data: Dict):
        with LOCK:
            self.coll.delete_many({})
            docs = []
            for name, meta in data.items():
                doc = dict(meta)
                doc['name'] = name
                docs.append(doc)
            if docs:
                self.coll.insert_many(docs)

    def get_bot(self, name: str) -> Optional[Dict]:
        doc = self.coll.find_one({'name': name}, projection={'_id': False})
        if not doc:
            return None
        doc = dict(doc)
        doc.pop('name', None)
        return doc

    def set_bot(self, name: str, meta: Dict):
        doc = dict(meta)
        doc['name'] = name
        self.coll.replace_one({'name': name}, doc, upsert=True)

    def delete_bot(self, name: str):
        self.coll.delete_one({'name': name})

    def get_admins(self) -> List[int]:
        doc = self.meta.find_one({'key': 'admins'}, projection={'_id': False})
        if not doc:
            return []
        return doc.get('value', [])

    def add_admin(self, tg_id: int):
        cur = self.meta.find_one({'key': 'admins'})
        if not cur:
            self.meta.insert_one({'key': 'admins', 'value': [int(tg_id)]})
        else:
            vals = set(cur.get('value', []))
            vals.add(int(tg_id))
            self.meta.replace_one({'key': 'admins'}, {'key': 'admins', 'value': sorted(list(vals))}, upsert=True)

    def del_admin(self, tg_id: int):
        cur = self.meta.find_one({'key': 'admins'})
        if not cur:
            return
        vals = set(cur.get('value', []))
        if int(tg_id) in vals:
            vals.remove(int(tg_id))
            self.meta.replace_one({'key': 'admins'}, {'key': 'admins', 'value': sorted(list(vals))}, upsert=True)

    def get_premium_users(self) -> Dict[int, Dict]:
        doc = self.meta.find_one({'key': 'premium_data'}, projection={'_id': False})
        if not doc:
            return {}
        data = doc.get('value', {})
        return {int(k): v for k, v in data.items()}

    def add_premium_user(self, tg_id: int, category: str = 'silver', expires_at: Optional[str] = None):
        tg_id = int(tg_id)
        cur = self.meta.find_one({'key': 'premium_data'})
        data = cur.get('value', {}) if cur else {}
        data[str(tg_id)] = {
            'category': category,
            'expires_at': expires_at,
            'added_at': datetime.now().isoformat()
        }
        self.meta.replace_one({'key': 'premium_data'}, {'key': 'premium_data', 'value': data}, upsert=True)

    def remove_premium_user(self, tg_id: int):
        tg_id = int(tg_id)
        cur = self.meta.find_one({'key': 'premium_data'})
        if not cur:
            return
        data = cur.get('value', {})
        if str(tg_id) in data:
            del data[str(tg_id)]
            self.meta.replace_one({'key': 'premium_data'}, {'key': 'premium_data', 'value': data}, upsert=True)

    def get_premium_user(self, tg_id: int) -> Optional[Dict]:
        data = self.get_premium_users()
        return data.get(int(tg_id))

    def is_premium(self, tg_id: int) -> bool:
        user = self.get_premium_user(int(tg_id))
        if not user:
            return False
        expires_at = user.get('expires_at')
        if not expires_at:
            return True
        return datetime.fromisoformat(expires_at) > datetime.now()

    def get_premium_plan(self, tg_id: int) -> Optional[str]:
        """Get the premium plan type for a user."""
        user = self.get_premium_user(int(tg_id))
        if not user:
            return None
        expires_at = user.get('expires_at')
        if expires_at and datetime.fromisoformat(expires_at) <= datetime.now():
            return None
        return user.get('category')

    def admin_exists(self, tg_id: int) -> bool:
        """Check if a user is an admin."""
        return int(tg_id) in self.get_admins()

    def get_admin_only(self) -> bool:
        doc = self.meta.find_one({'key': 'admin_only'})
        if not doc:
            return False
        return doc.get('value', False)

    def set_admin_only(self, enabled: bool):
        self.meta.replace_one({'key': 'admin_only'}, {'key': 'admin_only', 'value': bool(enabled)}, upsert=True)

    def get_user_bots(self, user_id: int) -> int:
        """Count how many bots a user owns."""
        count = self.coll.count_documents({'owner_id': user_id})
        return count

    def save_redeem_code(self, code: str, plan: str, duration_days: int, user_limit: int):
        """Save a redeem code."""
        cur = self.meta.find_one({'key': 'redeem_codes'})
        codes = cur.get('value', {}) if cur else {}
        codes[code] = {
            'plan': plan,
            'duration_days': duration_days,
            'user_limit': user_limit,
            'created_at': datetime.now().isoformat(),
            'used_by': []
        }
        self.meta.replace_one({'key': 'redeem_codes'}, {'key': 'redeem_codes', 'value': codes}, upsert=True)

    def get_redeem_code(self, code: str) -> Optional[Dict]:
        """Get a redeem code."""
        cur = self.meta.find_one({'key': 'redeem_codes'})
        codes = cur.get('value', {}) if cur else {}
        return codes.get(code)

    def use_redeem_code(self, code: str, user_id: int) -> bool:
        """Mark a redeem code as used by a user. Returns True if successful."""
        cur = self.meta.find_one({'key': 'redeem_codes'})
        codes = cur.get('value', {}) if cur else {}
        if code not in codes:
            return False
        
        code_data = codes[code]
        used_by = code_data.get('used_by', [])
        
        # Check if user already used this code
        if user_id in used_by:
            return False
        
        # Check if code usage limit reached
        if len(used_by) >= code_data.get('user_limit', 1):
            return False
        
        # Add user to used_by list
        used_by.append(user_id)
        code_data['used_by'] = used_by
        self.meta.replace_one({'key': 'redeem_codes'}, {'key': 'redeem_codes', 'value': codes}, upsert=True)
        return True

    def delete_redeem_code(self, code: str):
        """Delete a redeem code."""
        cur = self.meta.find_one({'key': 'redeem_codes'})
        codes = cur.get('value', {}) if cur else {}
        if code in codes:
            del codes[code]
            self.meta.replace_one({'key': 'redeem_codes'}, {'key': 'redeem_codes', 'value': codes}, upsert=True)


class SQLiteStorage:
    """A simple SQLite-backed storage compatible with FileStorage/MongoStorage API."""
    def __init__(self, path: Path = BASE_DATA_DIR / 'bots.db'):
        import sqlite3
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        with LOCK:
            cur = self.conn.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS bots(name TEXT PRIMARY KEY, meta TEXT)''')
            cur.execute('''CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT)''')
            self.conn.commit()

    def _get_meta(self, key: str):
        cur = self.conn.cursor()
        cur.execute('SELECT value FROM meta WHERE key = ?', (key,))
        row = cur.fetchone()
        return row['value'] if row else None

    def _set_meta(self, key: str, value: str):
        with LOCK:
            cur = self.conn.cursor()
            cur.execute('REPLACE INTO meta(key,value) VALUES(?,?)', (key, value))
            self.conn.commit()

    def load(self) -> Dict:
        out = {}
        cur = self.conn.cursor()
        for row in cur.execute('SELECT name, meta FROM bots'):
            name, meta = row
            try:
                out[name] = json.loads(meta)
            except Exception:
                out[name] = {}
        # load meta keys into out using same names as FileStorage
        cur.execute('SELECT key, value FROM meta')
        for row in cur.fetchall():
            k, v = row['key'], row['value']
            try:
                out_key = '__' + k + '__' if k in ('admins', 'premium_data', 'admin_only', 'redeem_codes') else k
                out[out_key] = json.loads(v)
            except Exception:
                out[k] = v
        return out

    def save(self, data: Dict):
        # save bots
        with LOCK:
            cur = self.conn.cursor()
            cur.execute('DELETE FROM bots')
            for name, meta in data.items():
                if name.startswith('__'):
                    continue
                cur.execute('INSERT INTO bots(name,meta) VALUES(?,?)', (name, json.dumps(meta)))
            self.conn.commit()

    def get_bot(self, name: str) -> Optional[Dict]:
        cur = self.conn.cursor()
        cur.execute('SELECT meta FROM bots WHERE name = ?', (name,))
        row = cur.fetchone()
        if not row:
            return None
        try:
            return json.loads(row['meta'])
        except Exception:
            return {}

    def set_bot(self, name: str, meta: Dict):
        with LOCK:
            cur = self.conn.cursor()
            cur.execute('REPLACE INTO bots(name,meta) VALUES(?,?)', (name, json.dumps(meta)))
            self.conn.commit()

    def delete_bot(self, name: str):
        with LOCK:
            cur = self.conn.cursor()
            cur.execute('DELETE FROM bots WHERE name = ?', (name,))
            self.conn.commit()

    def get_admins(self) -> List[int]:
        import sqlite3
        val = self._get_meta('admins')
        if not val:
            return []
        try:
            data = json.loads(val)
            return [int(x) for x in data]
        except Exception:
            return []

    def add_admin(self, tg_id: int):
        vals = set(self.get_admins())
        vals.add(int(tg_id))
        self._set_meta('admins', json.dumps(sorted(list(vals))))

    def del_admin(self, tg_id: int):
        vals = set(self.get_admins())
        if int(tg_id) in vals:
            vals.remove(int(tg_id))
            self._set_meta('admins', json.dumps(sorted(list(vals))))

    def get_premium_users(self) -> Dict[int, Dict]:
        val = self._get_meta('premium_data')
        if not val:
            return {}
        try:
            data = json.loads(val)
            return {int(k): v for k, v in data.items()}
        except Exception:
            return {}

    def add_premium_user(self, tg_id: int, category: str = 'silver', expires_at: Optional[str] = None):
        tg_id = int(tg_id)
        data = self.get_premium_users()
        data[str(tg_id)] = {
            'category': category,
            'expires_at': expires_at,
            'added_at': datetime.now().isoformat()
        }
        self._set_meta('premium_data', json.dumps({str(k): v for k, v in data.items()}))

    def remove_premium_user(self, tg_id: int):
        tg_id = int(tg_id)
        data = self.get_premium_users()
        if str(tg_id) in data:
            del data[str(tg_id)]
            self._set_meta('premium_data', json.dumps(data))

    def get_premium_user(self, tg_id: int) -> Optional[Dict]:
        data = self.get_premium_users()
        return data.get(int(tg_id))

    def is_premium(self, tg_id: int) -> bool:
        user = self.get_premium_user(int(tg_id))
        if not user:
            return False
        expires_at = user.get('expires_at')
        if not expires_at:
            return True
        return datetime.fromisoformat(expires_at) > datetime.now()

    def get_premium_plan(self, tg_id: int) -> Optional[str]:
        user = self.get_premium_user(int(tg_id))
        if not user:
            return None
        expires_at = user.get('expires_at')
        if expires_at and datetime.fromisoformat(expires_at) <= datetime.now():
            return None
        return user.get('category')

    def admin_exists(self, tg_id: int) -> bool:
        return int(tg_id) in self.get_admins()

    def get_admin_only(self) -> bool:
        val = self._get_meta('admin_only')
        if not val:
            return False
        try:
            return json.loads(val)
        except Exception:
            return False

    def set_admin_only(self, enabled: bool):
        self._set_meta('admin_only', json.dumps(bool(enabled)))

    def get_user_bots(self, user_id: int) -> int:
        cur = self.conn.cursor()
        cur.execute('SELECT COUNT(*) as c FROM bots WHERE json_extract(meta, "$.owner_id") = ?', (user_id,))
        row = cur.fetchone()
        return int(row['c']) if row else 0

    def save_redeem_code(self, code: str, plan: str, duration_days: int, user_limit: int):
        codes = self._get_meta('redeem_codes')
        try:
            data = json.loads(codes) if codes else {}
        except Exception:
            data = {}
        data[code] = {
            'plan': plan,
            'duration_days': duration_days,
            'user_limit': user_limit,
            'created_at': datetime.now().isoformat(),
            'used_by': []
        }
        self._set_meta('redeem_codes', json.dumps(data))

    def get_redeem_code(self, code: str) -> Optional[Dict]:
        codes = self._get_meta('redeem_codes')
        try:
            data = json.loads(codes) if codes else {}
            return data.get(code)
        except Exception:
            return None

    def use_redeem_code(self, code: str, user_id: int) -> bool:
        codes = self._get_meta('redeem_codes')
        try:
            data = json.loads(codes) if codes else {}
        except Exception:
            return False
        if code not in data:
            return False
        code_data = data[code]
        used_by = code_data.get('used_by', [])
        if user_id in used_by:
            return False
        if len(used_by) >= code_data.get('user_limit', 1):
            return False
        used_by.append(user_id)
        code_data['used_by'] = used_by
        data[code] = code_data
        self._set_meta('redeem_codes', json.dumps(data))
        return True

    def delete_redeem_code(self, code: str):
        codes = self._get_meta('redeem_codes')
        try:
            data = json.loads(codes) if codes else {}
        except Exception:
            data = {}
        if code in data:
            del data[code]
            self._set_meta('redeem_codes', json.dumps(data))
