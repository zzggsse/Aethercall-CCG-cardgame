"""卡牌数据定义：随从、法术、英雄与套牌。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Card:
    """一张卡牌的静态定义。"""

    cid: str
    name: str
    cost: int
    kind: str  # "minion" | "spell"
    text: str = ""
    attack: int = 0
    health: int = 0
    keywords: tuple[str, ...] = ()
    targeting: str = "none"
    effects: tuple[dict[str, Any], ...] = ()
    deathrattle: tuple[dict[str, Any], ...] = ()
    rarity: str = "common"
    hero: str = "neutral"

    @property
    def is_minion(self) -> bool:
        return self.kind == "minion"

    @property
    def is_spell(self) -> bool:
        return self.kind == "spell"


@dataclass
class Hero:
    """英雄定义，含英雄技能。"""

    hid: str
    name: str
    class_name: str
    power_name: str
    power_text: str
    power_cost: int
    power_targeting: str
    power_effects: tuple[dict[str, Any], ...]
    deck: list[str] = field(default_factory=list)


def _minion(cid, name, cost, attack, health, text="", keywords=(), targeting="none",
            effects=(), deathrattle=(), hero="neutral", rarity="common"):
    return Card(cid, name, cost, "minion", text, attack, health, tuple(keywords),
                targeting, tuple(effects), tuple(deathrattle), rarity, hero)


def _spell(cid, name, cost, text, targeting="none", effects=(), hero="neutral", rarity="common"):
    return Card(cid, name, cost, "spell", text, 0, 0, (), targeting,
                tuple(effects), (), rarity, hero)


NEUTRAL_CARDS: list[Card] = [
    _minion("wisp", "萤火妖精", 0, 1, 1),
    _minion("murloc_raider", "浅滩掠夺者", 1, 2, 1),
    _minion("elven_archer", "林语射手", 1, 1, 1, "战吼：造成1点伤害。",
            targeting="any_character",
            effects=[{"type": "damage", "target": "chosen", "amount": 1}]),
    _minion("river_croc", "沼泽巨鳄", 2, 2, 3),
    _minion("bloodfen_raptor", "血沼奔龙", 2, 3, 2),
    _minion("loot_hoarder", "拾荒盗贼", 2, 2, 1, "亡语：抽一张牌。",
            deathrattle=[{"type": "draw", "target": "owner", "amount": 1}]),
    _minion("frostwolf_grunt", "霜爪卫兵", 2, 2, 2, "嘲讽。", keywords=("taunt",)),
    _minion("shattered_sun", "曦光祭司", 3, 3, 2, "战吼：使一个友方随从获得+1/+1。",
            targeting="friendly_minion",
            effects=[{"type": "buff", "target": "chosen", "attack": 1, "health": 1}]),
    _minion("ironfur_grizzly", "铁鬃巨熊", 3, 3, 3, "嘲讽。", keywords=("taunt",)),
    _minion("raid_leader", "战阵督军", 3, 2, 2, "你的其他随从攻击力+1。",
            keywords=("aura_attack",)),
    _minion("chillwind_yeti", "雪原巨汉", 4, 4, 5),
    _minion("sen_jin", "石盾守卫", 4, 3, 5, "嘲讽。", keywords=("taunt",)),
    _minion("gnomish_inventor", "机巧发明家", 4, 2, 4, "战吼：抽一张牌。",
            effects=[{"type": "draw", "target": "owner", "amount": 1}]),
    _minion("dark_iron", "熔炉铁匠", 4, 4, 4, "战吼：使一个随从获得+2攻击力。",
            targeting="any_minion",
            effects=[{"type": "buff", "target": "chosen", "attack": 2, "health": 0}]),
    _minion("stormwind_champion", "王庭勇士", 7, 6, 6, "你的其他随从获得+1/+1。",
            keywords=("aura_attack", "aura_health"), rarity="epic"),
    _minion("boulderfist_ogre", "獠牙巨魔", 6, 6, 7),
    _minion("war_golem", "钢铁战偶", 7, 7, 7),
    _minion("argent_squire", "银誓侍从", 1, 1, 1, "圣盾。", keywords=("divine_shield",)),
    _minion("wolfrider", "狼背突骑", 3, 3, 1, "冲锋。", keywords=("charge",)),
    _minion("abomination", "腐化缝合怪", 5, 4, 4, "嘲讽。亡语：对所有角色造成2点伤害。",
            keywords=("taunt",), rarity="rare",
            deathrattle=[{"type": "aoe", "target": "all_characters", "amount": 2}]),
    _minion("ysera", "星梦龙后", 9, 4, 12, "嘲讽。战吼：抽两张牌。",
            keywords=("taunt",), rarity="legendary",
            effects=[{"type": "draw", "target": "owner", "amount": 2}]),
]

MAGE_CARDS: list[Card] = [
    _spell("fireball", "炽炎爆弹", 4, "造成6点伤害。", targeting="any_character",
           effects=[{"type": "damage", "target": "chosen", "amount": 6}], hero="mage"),
    _spell("frostbolt", "霜锥术", 2, "造成3点伤害并冻结目标。", targeting="any_character",
           effects=[{"type": "damage", "target": "chosen", "amount": 3},
                    {"type": "freeze", "target": "chosen"}], hero="mage"),
    _spell("arcane_missiles", "秘能弹幕", 1, "随机造成3点伤害。",
           effects=[{"type": "random_damage", "target": "enemy_characters", "amount": 3}],
           hero="mage"),
    _spell("flamestrike", "焚天火幕", 7, "对所有敌方随从造成5点伤害。",
           effects=[{"type": "aoe", "target": "enemy_minions", "amount": 5}],
           hero="mage", rarity="epic"),
    _spell("polymorph", "驯羊咒", 4, "将一个随从变为1/1的羔羊。", targeting="any_minion",
           effects=[{"type": "polymorph", "target": "chosen"}], hero="mage"),
    _minion("water_elemental", "寒潮元素", 4, 3, 6, "冻结受其伤害的角色。",
            keywords=("freeze_attacker",), hero="mage"),
    _spell("arcane_intellect", "秘典研读", 3, "抽两张牌。",
           effects=[{"type": "draw", "target": "owner", "amount": 2}], hero="mage"),
]

WARRIOR_CARDS: list[Card] = [
    _spell("shield_block", "铁壁架挡", 3, "获得5点护甲，抽一张牌。",
           effects=[{"type": "armor", "target": "owner", "amount": 5},
                    {"type": "draw", "target": "owner", "amount": 1}], hero="warrior"),
    _spell("execute", "处决令", 2, "消灭一个已受伤的敌方随从。", targeting="damaged_enemy_minion",
           effects=[{"type": "destroy", "target": "chosen"}], hero="warrior"),
    _spell("whirlwind", "回旋刃风", 1, "对所有随从造成1点伤害。",
           effects=[{"type": "aoe", "target": "all_minions", "amount": 1}], hero="warrior"),
    _spell("charge_spell", "突袭号令", 1, "使一个友方随从获得+2攻击力和冲锋。",
           targeting="friendly_minion",
           effects=[{"type": "buff", "target": "chosen", "attack": 2, "health": 0},
                    {"type": "grant", "target": "chosen", "keyword": "charge"}], hero="warrior"),
    _minion("armorsmith", "锻甲工匠", 2, 1, 4, "每当一个友方随从受到伤害，获得1点护甲。",
            keywords=("armorsmith",), hero="warrior", rarity="rare"),
    _minion("frothing_berserk", "嗜血狂徒", 3, 2, 4, "每当一个随从受到伤害，攻击力+1。",
            keywords=("frothing",), hero="warrior", rarity="epic"),
    _minion("kor_elite", "先锋精锐", 4, 4, 3, "冲锋。", keywords=("charge",), hero="warrior"),
]

PRIEST_CARDS: list[Card] = [
    _spell("holy_smite", "圣光谴击", 1, "造成2点伤害。", targeting="any_character",
           effects=[{"type": "damage", "target": "chosen", "amount": 2}], hero="priest"),
    _spell("power_word_shield", "庇护圣言", 1, "使一个随从获得+2生命值，抽一张牌。",
           targeting="any_minion",
           effects=[{"type": "buff", "target": "chosen", "attack": 0, "health": 2},
                    {"type": "draw", "target": "owner", "amount": 1}], hero="priest"),
    _spell("shadow_word_pain", "暗蚀低语", 2, "消灭一个攻击力小于等于3的随从。",
           targeting="weak_minion",
           effects=[{"type": "destroy", "target": "chosen"}], hero="priest"),
    _spell("holy_nova", "曦光新星", 5, "对敌方随从造成2点伤害，友方角色恢复2点生命。",
           effects=[{"type": "aoe", "target": "enemy_minions", "amount": 2},
                    {"type": "mass_heal", "target": "friendly_characters", "amount": 2}],
           hero="priest"),
    _minion("northshire_cleric", "晨钟修士", 1, 1, 3, "每当一个随从被治疗，抽一张牌。",
            keywords=("cleric",), hero="priest"),
    _minion("temple_enforcer", "圣殿卫士", 6, 6, 6, "战吼：使一个友方随从获得+3生命值。",
            targeting="friendly_minion",
            effects=[{"type": "buff", "target": "chosen", "attack": 0, "health": 3}],
            hero="priest"),
    _spell("mind_blast", "心灵冲击", 2, "对敌方英雄造成5点伤害。",
           effects=[{"type": "damage", "target": "enemy_hero", "amount": 5}], hero="priest"),
]

HUNTER_CARDS: list[Card] = [
    _spell("arcane_shot", "秘能冷箭", 1, "造成2点伤害。", targeting="any_character",
           effects=[{"type": "damage", "target": "chosen", "amount": 2}], hero="hunter"),
    _spell("kill_command", "猎杀号令", 3, "造成5点伤害。", targeting="any_character",
           effects=[{"type": "damage", "target": "chosen", "amount": 5}], hero="hunter"),
    _spell("multi_shot", "散射连箭", 4, "对两个随机敌方随从造成3点伤害。",
           effects=[{"type": "random_split", "target": "enemy_minions", "amount": 3, "times": 2}],
           hero="hunter"),
    _spell("unleash", "群兽奔袭", 3, "为每个敌方随从召唤一只1/1的恶犬，具有冲锋。",
           effects=[{"type": "summon_per_enemy", "token": "hound"}], hero="hunter"),
    _minion("houndmaster", "驭兽宗师", 4, 4, 3, "战吼：使一个友方随从获得+2/+2和嘲讽。",
            targeting="friendly_minion",
            effects=[{"type": "buff", "target": "chosen", "attack": 2, "health": 2},
                     {"type": "grant", "target": "chosen", "keyword": "taunt"}], hero="hunter"),
    _minion("savannah_highmane", "草原鬃王", 6, 6, 5, "亡语：召唤两只2/2的鬣兽。",
            deathrattle=[{"type": "summon", "token": "hyena", "count": 2}],
            hero="hunter", rarity="rare"),
    _minion("timber_wolf", "林间苍狼", 1, 1, 1, "你的其他随从攻击力+1。",
            keywords=("aura_attack",), hero="hunter"),
]

TOKENS: dict[str, Card] = {
    "sheep": _minion("sheep", "驯顺羔羊", 1, 1, 1),
    "hound": _minion("hound", "猎场恶犬", 1, 1, 1, "冲锋。", keywords=("charge",)),
    "hyena": _minion("hyena", "斑纹鬣兽", 2, 2, 2),
}

ALL_CARDS: dict[str, Card] = {}
for _c in NEUTRAL_CARDS + MAGE_CARDS + WARRIOR_CARDS + PRIEST_CARDS + HUNTER_CARDS:
    ALL_CARDS[_c.cid] = _c
ALL_CARDS.update(TOKENS)


def _deck(class_cards: list[str], neutrals: list[str]) -> list[str]:
    """每张牌两张，构成 30 张套牌。"""
    deck: list[str] = []
    for cid in class_cards + neutrals:
        deck.extend([cid, cid])
    return deck[:30]


HEROES: dict[str, Hero] = {
    "mage": Hero(
        "mage", "塞拉菲娜·晨曜", "法师", "烈焰灼击", "造成1点伤害。", 2, "any_character",
        ({"type": "damage", "target": "chosen", "amount": 1},),
        _deck([c.cid for c in MAGE_CARDS],
              ["wisp", "elven_archer", "bloodfen_raptor", "loot_hoarder", "river_croc",
               "chillwind_yeti", "gnomish_inventor", "sen_jin", "boulderfist_ogre"]),
    ),
    "warrior": Hero(
        "warrior", "格洛姆·裂颅", "战士", "披甲备战", "获得2点护甲。", 2, "none",
        ({"type": "armor", "target": "owner", "amount": 2},),
        _deck([c.cid for c in WARRIOR_CARDS],
              ["frostwolf_grunt", "ironfur_grizzly", "wolfrider", "murloc_raider",
               "chillwind_yeti", "sen_jin", "abomination", "war_golem"]),
    ),
    "priest": Hero(
        "priest", "艾德林·圣言", "牧师", "抚慰之光", "恢复2点生命。", 2, "any_character",
        ({"type": "heal", "target": "chosen", "amount": 2},),
        _deck([c.cid for c in PRIEST_CARDS],
              ["argent_squire", "river_croc", "shattered_sun", "loot_hoarder",
               "chillwind_yeti", "sen_jin", "boulderfist_ogre", "ysera"]),
    ),
    "hunter": Hero(
        "hunter", "卡兰·荒踪", "猎人", "精准狙击", "对敌方英雄造成2点伤害。", 2, "none",
        ({"type": "damage", "target": "enemy_hero", "amount": 2},),
        _deck([c.cid for c in HUNTER_CARDS],
              ["murloc_raider", "bloodfen_raptor", "wolfrider", "raid_leader",
               "ironfur_grizzly", "chillwind_yeti", "gnomish_inventor", "war_golem"]),
    ),
}


def get_card(cid: str) -> Card:
    return ALL_CARDS[cid]
