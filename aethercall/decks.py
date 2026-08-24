"""套牌存档：把玩家自建的牌库保存到本地 JSON 文件。"""

from __future__ import annotations

import json
from pathlib import Path

from .cards import DECK_SIZE, HEROES, validate_deck

SAVE_PATH = Path(__file__).resolve().parent.parent / "decks.json"


def load_all() -> dict[str, list[str]]:
    """读取全部自定义套牌，键为英雄 ID。"""
    if not SAVE_PATH.exists():
        return {}
    try:
        raw = json.loads(SAVE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    result: dict[str, list[str]] = {}
    for hero_id, deck in raw.items():
        if hero_id not in HEROES or not isinstance(deck, list):
            continue
        ok, _ = validate_deck(hero_id, deck)
        if ok:
            result[hero_id] = list(deck)
    return result


def save_deck(hero_id: str, deck: list[str]) -> tuple[bool, str]:
    """保存某英雄的自定义套牌，写入前会做合法性校验。"""
    ok, msg = validate_deck(hero_id, deck)
    if not ok:
        return False, msg
    data = load_all()
    data[hero_id] = list(deck)
    try:
        SAVE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as exc:
        return False, f"保存失败：{exc}"
    return True, f"套牌已保存（{DECK_SIZE} 张）。"


def delete_deck(hero_id: str) -> None:
    """删除某英雄的自定义套牌，恢复使用预组套牌。"""
    data = load_all()
    if hero_id in data:
        del data[hero_id]
        try:
            SAVE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                                 encoding="utf-8")
        except OSError:
            pass


def deck_for(hero_id: str) -> list[str]:
    """取得实际使用的套牌：优先自定义，否则用预组。"""
    custom = load_all().get(hero_id)
    if custom:
        return list(custom)
    return list(HEROES[hero_id].deck)


def has_custom(hero_id: str) -> bool:
    return hero_id in load_all()
