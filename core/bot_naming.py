# Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb
import re
import secrets
import string
from typing import Optional
from urllib.parse import urlparse


def extract_repo_name(repo_url: str) -> str:
    """
    Extract repository name from GitHub URL.
    
    Examples:
    - https://github.com/user/my-bot -> my-bot
    - https://github.com/user/my-bot.git -> my-bot
    - git@github.com:user/my-bot.git -> my-bot
    """
    repo_url = repo_url.strip()
    
    # Remove .git suffix if present
    if repo_url.endswith('.git'):
        repo_url = repo_url[:-4]
    
    # Handle SSH URLs (git@github.com:user/repo)
    if '@' in repo_url and ':' in repo_url:
        parts = repo_url.split(':')[-1].split('/')
        return parts[-1]
    
    # Handle HTTPS URLs
    try:
        parsed = urlparse(repo_url)
        path_parts = parsed.path.strip('/').split('/')
        if path_parts:
            return path_parts[-1]
    except Exception:
        pass
    
    # Fallback: get last part after splitting by /
    return repo_url.split('/')[-1]


def generate_random_hash(length: int = 6) -> str:
    """Generate a random alphanumeric hash."""
    chars = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def generate_bot_name(repo_url: str, user_id: int, username: Optional[str] = None) -> str:
    """
    Generate a unique bot name following the pattern:
    RepoName-Username[tg]-Hash[random]
    
    Example:
    - my-bot-john_doe123456-a1b2c3
    - my-awesome-bot-alice456789-x9y8z7
    """
    # Extract repo name
    repo_name = extract_repo_name(repo_url)
    
    # Sanitize repo name (remove special chars, keep hyphens and underscores)
    repo_name = re.sub(r'[^a-zA-Z0-9_-]', '', repo_name)
    repo_name = repo_name.lower()[:20]  # Limit length
    
    # Create user identifier
    if username:
        # Sanitize username
        user_id_part = re.sub(r'[^a-zA-Z0-9_]', '', username)
        user_id_part = user_id_part.lower()[:15]
        user_id_part += str(user_id)
    else:
        # Use just the user ID if no username
        user_id_part = str(user_id)
    
    # Generate random hash
    random_hash = generate_random_hash(6)
    
    # Combine into bot name
    bot_name = f"{repo_name}-{user_id_part}-{random_hash}"
    
    # Ensure it doesn't exceed typical length limits and is valid
    bot_name = bot_name[:60]  # Max length safety
    
    return bot_name
