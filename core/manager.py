# Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb

import logging
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from config import BASE_DATA_DIR, MONGO_URI, MONGO_DB, OWNER_IDS
from .storage import get_storage
from .deployer import Deployer, normalize_repo_url

logger = logging.getLogger('master.manager')


class BotManager:
    def __init__(self, data_dir: Path = BASE_DATA_DIR):
        self.data_dir = Path(data_dir)
        try:
            self.storage = get_storage()
            logger.info('Using storage backend: %s', type(self.storage).__name__)
        except Exception as e:
            logger.warning('Storage init failed, falling back to FileStorage: %s', e)
            from .storage import FileStorage
            self.storage = FileStorage(self.data_dir / 'bots.json')
        self.deployer = Deployer(self.data_dir / 'repos')
        self._processes: Dict[str, subprocess.Popen] = {}

    def list_bots(self) -> Dict:
        return self.storage.load()

    def register_bot(self, name: str, repo_url: str, branch: str = 'main', start_command: str = 'python bot.py', owner_id: int = None) -> Dict:
        d = self.list_bots()
        if name in d:
            raise KeyError('bot exists')
        normalized_url = normalize_repo_url(repo_url)
        try:
            path = self.deployer.clone_or_update(name, normalized_url, branch)
        except Exception:
            path = self.deployer.clone_or_update(name, repo_url, branch)
        try:
            self.deployer.prepare_env(name)
        except Exception:
            logger.exception('prepare_env failed during register for %s', name)
        proc = None
        status = 'stopped'
        try:
            proc = self.deployer.run_command(name, start_command)
            self._processes[name] = proc
            status = 'running'
        except Exception:
            logger.exception('Failed to start bot after register: %s', name)
        meta = {'repo_url': normalized_url, 'branch': branch, 'start_command': start_command, 'status': status}
        if owner_id:
            meta['owner_id'] = owner_id
        if proc:
            meta['pid'] = proc.pid
        self.storage.set_bot(name, meta)
        return meta

    def start(self, name: str) -> Dict:
        meta = self.storage.get_bot(name)
        if not meta:
            raise KeyError('not found')
        if name in self._processes and self._processes[name].poll() is None:
            raise RuntimeError('already running')
        self.deployer.clone_or_update(name, meta['repo_url'], meta.get('branch', 'main'))
        try:
            self.deployer.prepare_env(name)
        except Exception:
            logger.exception('prepare_env failed during start for %s', name)
        proc = self.deployer.run_command(name, meta.get('start_command', 'python bot.py'))
        self._processes[name] = proc
        meta['status'] = 'running'
        meta['pid'] = proc.pid
        self.storage.set_bot(name, meta)
        return {'pid': proc.pid}

    def stop(self, name: str) -> Dict:
        proc = self._processes.get(name)
        if not proc:
            raise RuntimeError('not running')
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()
        del self._processes[name]
        meta = self.storage.get_bot(name)
        if meta:
            meta['status'] = 'stopped'
            meta.pop('pid', None)
            self.storage.set_bot(name, meta)
        return {'stopped': True}

    def restart(self, name: str) -> Dict:
        if name in self._processes:
            self.stop(name)
        return self.start(name)

    def switch_branch(self, name: str, branch: str) -> Dict:
        meta = self.storage.get_bot(name)
        if not meta:
            raise KeyError('not found')
        self.deployer.checkout_branch(name, branch)
        meta['branch'] = branch
        meta['status'] = 'stopped'
        meta.pop('pid', None)
        self.storage.set_bot(name, meta)
        return {'switched': True}

    def delete_bot(self, name: str) -> Dict:
        proc = self._processes.get(name)
        if proc:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
            del self._processes[name]
        repo_path = self.deployer.bot_dir(name)
        if repo_path.exists():
            shutil.rmtree(repo_path)
        self.storage.delete_bot(name)
        return {'removed': True}

    def get_admins(self) -> List[int]:
        return self.storage.get_admins()

    def add_admin(self, tg_id: int):
        self.storage.add_admin(int(tg_id))

    def del_admin(self, tg_id: int):
        self.storage.del_admin(int(tg_id))
