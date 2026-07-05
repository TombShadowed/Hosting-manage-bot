import os
import sys
import shlex
import subprocess
import shutil
# Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb
import logging
from pathlib import Path
from git import Repo
from git.exc import GitCommandError
from typing import Optional, Dict

logger = logging.getLogger('master.deployer')


def normalize_repo_url(repo_url: str) -> str:
    if not repo_url:
        return repo_url
    repo_url = repo_url.strip()
    if 'raw.githubusercontent.com' in repo_url:
        parts = repo_url.split('/')
        if len(parts) >= 3:
            owner = parts[1]
            repo = parts[2]
            return f'https://github.com/{owner}/{repo}'
        return repo_url
    for seg in ('/blob/', '/tree/'):
        if seg in repo_url:
            idx = repo_url.find(seg)
            return repo_url[:idx].rstrip('/')
    return repo_url


class Deployer:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def bot_dir(self, name: str) -> Path:
        return (self.base_dir / name).resolve()

    def clone_or_update(self, name: str, repo_url: str, branch: str = 'main') -> str:
        path = self.bot_dir(name)
        if path.exists() and (path / '.git').exists():
            logger.info('Updating repo %s', name)
            repo = Repo(path)
            try:
                repo.remotes.origin.fetch()
                repo.git.checkout(branch)
                repo.remotes.origin.pull(branch)
            except Exception as e:
                logger.warning('Git update failed: %s', e)
            return str(path)

        if path.exists():
            shutil.rmtree(path)
        logger.info('Cloning %s -> %s', repo_url, path)
        try:
            repo = Repo.clone_from(repo_url, path, branch=branch)
            return str(repo.working_tree_dir)
        except GitCommandError as e:
            msg = str(e)
            if ('Write access to repository not granted' in msg
                    or 'The requested URL returned error: 403' in msg
                    or 'fatal: unable to access' in msg):
                raise RuntimeError(
                    "Unable to clone your repo. Please check if it's public or private. "
                    "If it's public, kindly report the issue to the developer. "
                    "If it's private, use your git token to clone it, for example: "
                    "/register bot1 git clone https://<github_pat_token>@github.com/username/repo main python3 bot.py"
                ) from e
            raise

    def prepare_env(self, name: str):
        path = self.bot_dir(name)
        if not path.exists():
            raise FileNotFoundError(f'Repo path not found: {path}')
        self._prepare_env_after_clone(path)

    def checkout_branch(self, name: str, branch: str) -> str:
        path = self.bot_dir(name)
        repo = Repo(path)
        origin = repo.remotes.origin
        origin.fetch()
        repo.git.checkout(branch)
        origin.pull(branch)
        return str(path)

    def run_command(self, name: str, command: str, env: Optional[Dict] = None) -> subprocess.Popen:
        path = self.bot_dir(name)
        if isinstance(command, str):
            cmd_list = shlex.split(command)
        else:
            cmd_list = command
        logs = path / 'logs'
        logs.mkdir(parents=True, exist_ok=True)
        stdout = open(logs / 'out.log', 'a', encoding='utf-8')
        stderr = open(logs / 'err.log', 'a', encoding='utf-8')
        env_map = os.environ.copy()
        if env:
            env_map.update(env)
        venv_bin = path / '1' / 'bin'
        replaced_python = False
        if venv_bin.exists():
            env_map.setdefault('VIRTUAL_ENV', str(path / '1'))
            env_map['PATH'] = str(venv_bin) + os.pathsep + env_map.get('PATH', '')
            try:
                venv_python = path / '1' / 'bin' / 'python'
                if cmd_list:
                    prog = os.path.basename(cmd_list[0])
                    if prog.startswith('python'):
                        if venv_python.exists():
                            cmd_list[0] = str(venv_python)
                            if '-u' not in cmd_list:
                                cmd_list.insert(1, '-u')
                            replaced_python = True
                        else:
                            env_map.setdefault('PYTHONUNBUFFERED', '1')
            except Exception:
                pass
        proc = subprocess.Popen(cmd_list, cwd=str(path), stdout=stdout, stderr=stderr, env=env_map)
        return proc

    def _prepare_env_after_clone(self, path: Path):
        req_file = path / 'requirements.txt'
        venv_dir = path / '1'
        logs = path / 'logs'
        logs.mkdir(parents=True, exist_ok=True)
        install_out = logs / 'install_out.log'
        install_err = logs / 'install_err.log'
        try:
            def make_venv():
                logger.info('Creating venv at %s', venv_dir)
                with open(install_out, 'a', encoding='utf-8') as outf, open(install_err, 'a', encoding='utf-8') as errf:
                    subprocess.run([sys.executable, '-m', 'venv', str(venv_dir)], check=True, stdout=outf, stderr=errf)

            if not venv_dir.exists():
                make_venv()
            else:
                venv_python = venv_dir / 'bin' / 'python'
                if not venv_python.exists():
                    logger.warning('venv python not found, recreating')
                    shutil.rmtree(venv_dir, ignore_errors=True)
                    make_venv()
                else:
                    try:
                        with open(install_out, 'a', encoding='utf-8') as outf, open(install_err, 'a', encoding='utf-8') as errf:
                            subprocess.run([str(venv_python), '--version'], check=True, stdout=outf, stderr=errf)
                    except Exception as e:
                        logger.warning('venv python check failed, recreating: %s', e)
                        try:
                            shutil.rmtree(venv_dir, ignore_errors=True)
                        except Exception:
                            pass
                        make_venv()

            venv_python = venv_dir / 'bin' / 'python'
            py_exe = str(venv_python) if venv_python.exists() else sys.executable
            logger.info('Using Python: %s', py_exe)

            logger.info('Upgrading pip in venv')
            tried_rebuild = False
            try:
                with open(install_out, 'a', encoding='utf-8') as outf, open(install_err, 'a', encoding='utf-8') as errf:
                    subprocess.run([py_exe, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True, stdout=outf, stderr=errf)
            except Exception as e:
                logger.warning('pip upgrade failed: %s', e)
                if not tried_rebuild:
                    tried_rebuild = True
                    try:
                        logger.info('Rebuilding venv after pip failure')
                        if venv_dir.exists():
                            shutil.rmtree(venv_dir, ignore_errors=True)
                        make_venv()
                        venv_python = venv_dir / 'bin' / 'python'
                        py_exe = str(venv_python) if venv_python.exists() else sys.executable
                        with open(install_out, 'a', encoding='utf-8') as outf, open(install_err, 'a', encoding='utf-8') as errf:
                            subprocess.run([py_exe, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True, stdout=outf, stderr=errf)
                    except Exception as e2:
                        logger.error('pip upgrade failed after rebuild: %s', e2)

            if req_file.exists():
                logger.info('Installing requirements from %s', req_file)
                with open(install_out, 'a', encoding='utf-8') as outf, open(install_err, 'a', encoding='utf-8') as errf:
                    subprocess.run([py_exe, '-m', 'pip', 'install', '-r', str(req_file)], check=True, stdout=outf, stderr=errf)
                logger.info('Requirements installed successfully')
            else:
                logger.warning('requirements.txt not found at %s', req_file)
        except Exception as e:
            logger.error('Failed to prepare env: %s', e)
            with open(install_err, 'a', encoding='utf-8') as f:
                import traceback
                traceback.print_exc(file=f)
