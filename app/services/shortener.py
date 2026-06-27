from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

BASE62_CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def base62_encode(num: int) -> str:
    if num < 0:
        raise ValueError("num must be non-negative")
    if num == 0:
        return BASE62_CHARS[0]

    chars: list[str] = []
    while num:
        num, remainder = divmod(num, 62)
        chars.append(BASE62_CHARS[remainder])
    return "".join(reversed(chars))


async def generate_short_code(db: AsyncSession) -> str:
    result = await db.execute(text("SELECT nextval('url_id_seq')"))
    seq_id = result.scalar_one()
    code = base62_encode(seq_id)
    pad_length = settings.SHORT_CODE_LENGTH - len(code)
    if pad_length > 0:
        code = BASE62_CHARS[0] * pad_length + code
    return code
