# Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb

import random
import string


def generate_redeem_code(length: int = 10) -> str:
    """Generate a random redeem code using uppercase letters and digits."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))
