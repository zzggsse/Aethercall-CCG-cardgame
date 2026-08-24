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


# ---------- 扩充卡池：中立 ----------

NEUTRAL_EXTRA: list[Card] = [
    _minion("mana_wyrm_n", "灵能雏龙", 1, 1, 3, "嘲讽。", keywords=("taunt",)),
    _minion("dune_scout", "沙丘斥候", 1, 2, 1, "战吼：抽一张牌。",
            effects=[{"type": "draw", "target": "owner", "amount": 1}], rarity="rare"),
    _minion("lantern_bearer", "提灯信使", 1, 1, 2, "亡语：使一个随机友方随从获得+1/+1。",
            deathrattle=[{"type": "random_buff", "target": "friendly_minions",
                          "attack": 1, "health": 1}]),
    _minion("rustblade_rogue", "锈刃游侠", 2, 3, 2),
    _minion("stone_sentry", "磐石哨兵", 2, 1, 4, "嘲讽。", keywords=("taunt",)),
    _minion("ember_imp", "灰烬小鬼", 2, 3, 1, "战吼：对敌方英雄造成1点伤害。",
            effects=[{"type": "damage", "target": "enemy_hero", "amount": 1}]),
    _minion("tide_priestess", "潮汐女祭司", 2, 2, 2, "战吼：恢复3点生命。",
            targeting="any_character",
            effects=[{"type": "heal", "target": "chosen", "amount": 3}]),
    _minion("cog_tinkerer", "齿轮修补匠", 2, 2, 2, "亡语：抽一张牌。",
            deathrattle=[{"type": "draw", "target": "owner", "amount": 1}], rarity="rare"),
    _minion("thorn_bristle", "针刺魔藤", 3, 2, 4, "嘲讽。圣盾。",
            keywords=("taunt", "divine_shield"), rarity="rare"),
    _minion("windstep_duelist", "疾风决斗者", 3, 2, 3, "风怒。", keywords=("windfury",),
            rarity="rare"),
    _minion("grave_warden", "陵墓守卫", 3, 3, 3, "亡语：召唤一个2/2的墓仆。",
            deathrattle=[{"type": "summon", "token": "tomb_servant", "count": 1}]),
    _minion("flame_juggler", "火焰杂技师", 3, 3, 2, "战吼：随机造成2点伤害。",
            effects=[{"type": "random_damage", "target": "enemy_characters", "amount": 2}]),
    _minion("oath_shield", "誓约盾卫", 3, 2, 5, "嘲讽。", keywords=("taunt",)),
    _minion("crystal_scholar", "水晶学者", 3, 2, 3, "战吼：抽一张牌。",
            effects=[{"type": "draw", "target": "owner", "amount": 1}]),
    _minion("dusk_stalker", "暮色潜行者", 4, 5, 3),
    _minion("iron_bulwark", "铁壁堡卫", 4, 2, 7, "嘲讽。", keywords=("taunt",), rarity="rare"),
    _minion("banner_captain", "旌旗队长", 4, 3, 4, "你的其他随从攻击力+1。",
            keywords=("aura_attack",), rarity="rare"),
    _minion("plague_rat", "疫病巨鼠", 4, 3, 3, "亡语：对所有其他随从造成1点伤害。",
            deathrattle=[{"type": "aoe", "target": "all_minions", "amount": 1}]),
    _minion("moon_oracle", "皓月先知", 4, 3, 4, "战吼：抽一张牌并恢复2点生命。",
            effects=[{"type": "draw", "target": "owner", "amount": 1},
                     {"type": "heal", "target": "owner", "amount": 2}]),
    _minion("gilded_guardian", "鎏金守护者", 5, 4, 5, "圣盾。嘲讽。",
            keywords=("divine_shield", "taunt"), rarity="epic"),
    _minion("storm_herald", "风暴先驱", 5, 4, 4, "战吼：使一个友方随从获得风怒。",
            targeting="friendly_minion",
            effects=[{"type": "grant", "target": "chosen", "keyword": "windfury"}],
            rarity="rare"),
    _minion("bone_colossus", "白骨巨像", 5, 6, 4, "亡语：召唤两个2/2的墓仆。",
            deathrattle=[{"type": "summon", "token": "tomb_servant", "count": 2}],
            rarity="rare"),
    _minion("mirror_construct", "镜影构造体", 5, 5, 5),
    _minion("frost_titan", "霜寒泰坦", 6, 5, 6, "战吼：冻结一个敌方随从。",
            targeting="enemy_minion",
            effects=[{"type": "freeze", "target": "chosen"}], rarity="rare"),
    _minion("verdant_ancient", "苍翠古树", 6, 4, 8, "嘲讽。", keywords=("taunt",)),
    _minion("hall_champion", "殿堂勇士", 6, 5, 5, "战吼：使你的其他随从获得+1/+1。",
            effects=[{"type": "buff", "target": "friendly_minions", "attack": 1, "health": 1}],
            rarity="epic"),
    _minion("void_devourer", "虚空噬灵者", 7, 7, 6, "战吼：消灭一个已受伤的敌方随从。",
            targeting="damaged_enemy_minion",
            effects=[{"type": "destroy", "target": "chosen"}], rarity="epic"),
    _minion("sky_leviathan", "天穹利维坦", 8, 8, 8, "嘲讽。", keywords=("taunt",),
            rarity="epic"),
    _minion("eternal_archon", "永恒执政官", 9, 8, 8, "圣盾。嘲讽。战吼：抽两张牌。",
            keywords=("divine_shield", "taunt"), rarity="legendary",
            effects=[{"type": "draw", "target": "owner", "amount": 2}]),
    _minion("worldbreaker", "碎界巨兽", 10, 10, 10, "战吼：对所有敌方随从造成3点伤害。",
            effects=[{"type": "aoe", "target": "enemy_minions", "amount": 3}],
            rarity="legendary"),
]
# ---------- 扩充卡池：职业 ----------

MAGE_EXTRA: list[Card] = [
    _spell("arcane_bolt", "秘能冲击", 1, "造成2点伤害。抽一张牌。", targeting="any_character",
           effects=[{"type": "damage", "target": "chosen", "amount": 2},
                    {"type": "draw", "target": "owner", "amount": 1}], hero="mage", rarity="rare"),
    _spell("frost_nova", "冰霜新星", 3, "冻结所有敌方随从。",
           effects=[{"type": "freeze", "target": "enemy_minions"}], hero="mage"),
    _spell("mana_surge", "法力涌动", 2, "获得一个法力水晶，抽一张牌。",
           effects=[{"type": "give_mana", "target": "owner", "amount": 1},
                    {"type": "draw", "target": "owner", "amount": 1}], hero="mage", rarity="rare"),
    _spell("cinder_storm", "余烬风暴", 5, "对所有敌方角色造成3点伤害。",
           effects=[{"type": "aoe", "target": "enemy_characters", "amount": 3}], hero="mage",
           rarity="rare"),
    _spell("mirror_image", "镜像术", 1, "召唤两个1/1的镜像，具有嘲讽。",
           effects=[{"type": "summon", "token": "mirror_minion", "count": 2}], hero="mage"),
    _spell("combustion", "爆破术", 6, "造成8点伤害，随机分配到所有敌方随从。",
           effects=[{"type": "random_split", "target": "enemy_minions", "amount": 1, "times": 8}],
           hero="mage", rarity="epic"),
    _minion("sorcerer_app", "奥术学徒", 2, 3, 2, "你的法术消耗减少1点（不能少于1）。",
            keywords=("spell_cost_down",), hero="mage", rarity="rare"),
    _minion("frost_elemental", "冰霜元素", 5, 4, 5, "冻结受其伤害的角色。",
            keywords=("freeze_attacker",), hero="mage"),
    _minion("arcane_giant", "奥术巨人", 8, 6, 8, "本局每施放一个法术，消耗减少1。",
            keywords=("arcane_cost",), hero="mage", rarity="epic"),
    _minion("pyromancer", "烈焰术士", 3, 3, 3, "战吼：对所有敌方随从造成1点伤害。",
            effects=[{"type": "aoe", "target": "enemy_minions", "amount": 1}], hero="mage"),
    _minion("crystal_invoker", "水晶唤法者", 4, 3, 5, "法术伤害+1。",
            keywords=("spell_power",), hero="mage", rarity="rare"),
    _minion("archmage_essence", "大法师·源质", 7, 5, 7, "战吼：将3张随机法师法术加入手牌。",
            effects=[{"type": "add_random_class_spells", "hero": "mage", "count": 3}],
            hero="mage", rarity="legendary"),
    _spell("ice_lance", "冰枪术", 1, "对一个单位造成3点伤害。如果目标已被冻结，改为6点。",
           targeting="any_character",
           effects=[{"type": "conditional_damage", "target": "chosen", "amount": 3,
                     "if_frozen": 6}], hero="mage", rarity="rare"),
]

WARRIOR_EXTRA: list[Card] = [
    _spell("battle_shout", "战吼", 1, "使一个友方随从获得+2攻击力。", targeting="friendly_minion",
           effects=[{"type": "buff", "target": "chosen", "attack": 2, "health": 0}],
           hero="warrior"),
    _spell("sundering_blow", "破甲重击", 3, "消灭一个敌方随从，并获得3点护甲。",
           targeting="enemy_minion",
           effects=[{"type": "destroy", "target": "chosen"},
                    {"type": "armor", "target": "owner", "amount": 3}], hero="warrior",
           rarity="rare"),
    _spell("battle_roar", "战斗怒吼", 2, "使你所有随从获得+1攻击力，抽一张牌。",
           effects=[{"type": "buff", "target": "friendly_minions", "attack": 1, "health": 0},
                    {"type": "draw", "target": "owner", "amount": 1}], hero="warrior"),
    _spell("shield_bash", "盾击", 2, "造成等同于你护甲值的伤害。", targeting="any_character",
           effects=[{"type": "armor_damage", "target": "chosen"}], hero="warrior"),
    _spell("mortal_strike", "致死打击", 4, "造成4点伤害。如果你的英雄生命≤12，改为6点。",
           targeting="any_character",
           effects=[{"type": "conditional_damage", "target": "chosen", "amount": 4,
                     "if_hero_below": 12, "then": 6}], hero="warrior", rarity="rare"),
    _minion("shield_maiden", "盾甲女卫", 5, 4, 5, "战吼：获得4点护甲。",
            effects=[{"type": "armor", "target": "owner", "amount": 4}], hero="warrior"),
    _minion("battle_chanter", "战歌祭司", 3, 2, 3, "你的其他随从获得冲锋。",
            keywords=("aura_charge",), hero="warrior", rarity="epic"),
    _minion("iron_captain", "铁血队长", 4, 4, 4, "战吼：使一个友方随从获得+1/+1和嘲讽。",
            targeting="friendly_minion",
            effects=[{"type": "buff", "target": "chosen", "attack": 1, "health": 1},
                     {"type": "grant", "target": "chosen", "keyword": "taunt"}], hero="warrior"),
    _minion("war_zealot", "战争狂徒", 2, 2, 2, "每当你获得护甲，该随从获得+1攻击力。",
            keywords=("armor_synergy",), hero="warrior", rarity="rare"),
    _minion("blade_dancer", "剑刃舞者", 4, 3, 5, "风怒。", keywords=("windfury",), hero="warrior"),
    _minion("forge_master", "锻造宗师", 6, 5, 5, "战吼：获得5点护甲，抽一张牌。",
            effects=[{"type": "armor", "target": "owner", "amount": 5},
                     {"type": "draw", "target": "owner", "amount": 1}], hero="warrior"),
    _minion("warlord_vanguard", "战帅·先锋", 7, 6, 6, "冲锋。战吼：获得3点护甲。",
            keywords=("charge",), hero="warrior", rarity="legendary",
            effects=[{"type": "armor", "target": "owner", "amount": 3}]),
    _spell("cleave", "顺劈斩", 2, "对两个随机敌方随从造成2点伤害。",
           effects=[{"type": "random_split", "target": "enemy_minions", "amount": 2, "times": 2}],
           hero="warrior"),
]

PRIEST_EXTRA: list[Card] = [
    _spell("healing_rain", "治愈之雨", 3, "恢复所有友方角色3点生命。",
           effects=[{"type": "mass_heal", "target": "friendly_characters", "amount": 3}],
           hero="priest"),
    _spell("inner_fire", "心灵之火", 1, "使一个随从的攻击力等于其生命值。",
           targeting="any_minion",
           effects=[{"type": "set_attack_to_health", "target": "chosen"}], hero="priest",
           rarity="common"),
    _spell("divine_spirit", "神圣之灵", 2, "使一个随从的生命值翻倍。", targeting="any_minion",
           effects=[{"type": "double_health", "target": "chosen"}], hero="priest"),
    _spell("silence_spell", "沉默术", 1, "沉默一个随从。", targeting="any_minion",
           effects=[{"type": "silence", "target": "chosen"}], hero="priest"),
    _spell("mass_dispel", "群体驱散", 4, "沉默所有敌方随从，抽一张牌。",
           effects=[{"type": "silence", "target": "enemy_minions"},
                    {"type": "draw", "target": "owner", "amount": 1}], hero="priest",
           rarity="rare"),
    _minion("light_whelp", "光明幼龙", 1, 1, 2, "战吼：恢复2点生命。", targeting="any_character",
            effects=[{"type": "heal", "target": "chosen", "amount": 2}], hero="priest"),
    _minion("shadow_adept", "暗影教徒", 2, 2, 3, "战吼：对一个敌方随从造成2点伤害。",
            targeting="enemy_minion",
            effects=[{"type": "damage", "target": "chosen", "amount": 2}], hero="priest"),
    _minion("holy_avenger", "圣洁复仇者", 3, 3, 4, "圣盾。", keywords=("divine_shield",),
            hero="priest"),
    _minion("ivory_priest", "象牙祭司", 4, 3, 5, "战吼：恢复所有友方角色3点生命。",
            effects=[{"type": "mass_heal", "target": "friendly_characters", "amount": 3}],
            hero="priest", rarity="rare"),
    _minion("dark_heretic", "黑暗异教徒", 5, 4, 5, "战吼：消灭一个攻击力≤3的敌方随从。",
            targeting="weak_minion",
            effects=[{"type": "destroy", "target": "chosen"}], hero="priest", rarity="rare"),
    _minion("prophet_veil", "先知·帷幔", 6, 5, 6, "战吼：抽三张牌。",
            effects=[{"type": "draw", "target": "owner", "amount": 3}], hero="priest",
            rarity="epic"),
    _minion("high_inquisitor", "大审判官", 7, 6, 6, "战吼：沉默所有敌方随从，恢复4点生命。",
            effects=[{"type": "silence", "target": "enemy_minions"},
                     {"type": "heal", "target": "owner", "amount": 4}], hero="priest",
            rarity="legendary"),
    _spell("shadow_word_death", "暗言术：灭", 3, "消灭一个攻击力≥5的随从。",
           targeting="strong_minion",
           effects=[{"type": "destroy", "target": "chosen"}], hero="priest"),
]

HUNTER_EXTRA: list[Card] = [
    _spell("hunter_mark", "猎人印记", 1, "使一个随从获得「受伤时被消灭」。（效果持续到回合结束）",
           targeting="any_minion",
           effects=[{"type": "mark", "target": "chosen"}], hero="hunter", rarity="rare"),
    _spell("explosive_trap", "爆炸陷阱", 2, "当你的英雄被攻击时，对所有敌方随从造成2点伤害。",
           effects=[{"type": "trap_explosive", "target": "none"}], hero="hunter", rarity="rare"),
    _spell("rapid_shot", "速射", 1, "造成3点伤害。", targeting="any_character",
           effects=[{"type": "damage", "target": "chosen", "amount": 3}], hero="hunter"),
    _spell("beast_call", "野兽召唤", 4, "召唤一个3/3的野兽。",
           effects=[{"type": "summon", "token": "beast_3_3", "count": 1}], hero="hunter"),
    _spell("storm_volley", "风暴箭雨", 6, "对所有敌方随从造成4点伤害。",
           effects=[{"type": "aoe", "target": "enemy_minions", "amount": 4}], hero="hunter",
           rarity="rare"),
    _minion("alpha_wolf", "头狼", 3, 3, 3, "你的其他随从获得+1攻击力。",
            keywords=("aura_attack",), hero="hunter"),
    _minion("eagle_eye", "鹰眼射手", 2, 2, 2, "战吼：造成2点伤害。", targeting="any_character",
            effects=[{"type": "damage", "target": "chosen", "amount": 2}], hero="hunter"),
    _minion("pack_leader", "兽群首领", 4, 3, 4, "战吼：召唤一只2/2的野兽。",
            effects=[{"type": "summon", "token": "beast_2_2", "count": 1}], hero="hunter"),
    _minion("silver_fang", "银牙猎手", 5, 4, 4, "战吼：召唤一只2/2的野兽，并使它获得冲锋。",
            effects=[{"type": "summon", "token": "beast_2_2_charge", "count": 1}],
            hero="hunter", rarity="rare"),
    _minion("great_wolf", "巨狼", 6, 5, 5, "战吼：使你的其他随从获得+2攻击力。",
            effects=[{"type": "buff", "target": "friendly_minions", "attack": 2, "health": 0}],
            hero="hunter", rarity="epic"),
    _minion("razor_feather", "刃羽战鹰", 4, 4, 2, "风怒。", keywords=("windfury",), hero="hunter"),
    _minion("beast_master", "驭兽之王", 7, 4, 6, "战吼：召唤两只3/3的野兽。",
            effects=[{"type": "summon", "token": "beast_3_3", "count": 2}], hero="hunter",
            rarity="legendary"),
    _spell("wing_storm", "翼风席卷", 5, "对所有敌方随从造成2点伤害，抽一张牌。",
           effects=[{"type": "aoe", "target": "enemy_minions", "amount": 2},
                    {"type": "draw", "target": "owner", "amount": 1}], hero="hunter", rarity="rare"),
]

DRUID_CARDS: list[Card] = [
    _spell("wild_growth", "野性成长", 2, "获得一个法力水晶。",
           effects=[{"type": "give_mana", "target": "owner", "amount": 1}], hero="druid"),
    _spell("claw_swipe", "利爪横扫", 2, "造成3点伤害，获得2点护甲。", targeting="any_character",
           effects=[{"type": "damage", "target": "chosen", "amount": 3},
                    {"type": "armor", "target": "owner", "amount": 2}], hero="druid"),
    _spell("nourish", "滋养", 5, "抽三张牌。",
           effects=[{"type": "draw", "target": "owner", "amount": 3}], hero="druid",
           rarity="rare"),
    _spell("mark_of_wild", "野性印记", 2, "使一个随从获得+2/+2和嘲讽。",
           targeting="friendly_minion",
           effects=[{"type": "buff", "target": "chosen", "attack": 2, "health": 2},
                    {"type": "grant", "target": "chosen", "keyword": "taunt"}], hero="druid"),
    _spell("starfall", "星落", 5, "对所有敌方随从造成3点伤害。",
           effects=[{"type": "aoe", "target": "enemy_minions", "amount": 3}], hero="druid",
           rarity="rare"),
    _spell("moonfire", "月火术", 0, "造成1点伤害。", targeting="any_character",
           effects=[{"type": "damage", "target": "chosen", "amount": 1}], hero="druid"),
    _minion("sapling", "幼苗守卫", 1, 1, 2, "嘲讽。", keywords=("taunt",), hero="druid"),
    _minion("grove_keeper", "林地看护者", 3, 2, 4, "战吼：获得3点护甲。",
            effects=[{"type": "armor", "target": "owner", "amount": 3}], hero="druid"),
    _minion("bear_form", "熊形态战士", 4, 4, 4, "嘲讽。", keywords=("taunt",), hero="druid"),
    _minion("thorn_beast", "荆棘巨兽", 5, 5, 5, "战吼：使一个友方随从获得+2/+2。",
            targeting="friendly_minion",
            effects=[{"type": "buff", "target": "chosen", "attack": 2, "health": 2}],
            hero="druid", rarity="rare"),
    _minion("ancient_protector", "远古庇护者", 6, 4, 9, "嘲讽。", keywords=("taunt",),
            hero="druid", rarity="rare"),
    _minion("treant_lord", "树人领主", 7, 6, 7, "战吼：召唤两个2/2的树人。",
            effects=[{"type": "summon", "token": "treant", "count": 2}], hero="druid",
            rarity="epic"),
    _minion("world_tree", "世界之树", 9, 7, 10, "嘲讽。战吼：使你的其他随从获得+2/+2。",
            keywords=("taunt",), hero="druid", rarity="legendary",
            effects=[{"type": "buff", "target": "friendly_minions", "attack": 2, "health": 2}]),
]

ROGUE_CARDS: list[Card] = [
    _spell("backstab", "背刺", 0, "对一个未受伤的随从造成2点伤害。",
           targeting="undamaged_minion",
           effects=[{"type": "damage", "target": "chosen", "amount": 2}], hero="rogue"),
    _spell("eviscerate", "刺骨", 2, "造成4点伤害。", targeting="any_character",
           effects=[{"type": "damage", "target": "chosen", "amount": 4}], hero="rogue"),
    _spell("sprint_spell", "疾跑", 6, "抽四张牌。",
           effects=[{"type": "draw", "target": "owner", "amount": 4}], hero="rogue",
           rarity="rare"),
    _spell("fan_of_knives", "刀扇", 3, "对所有敌方随从造成1点伤害，抽一张牌。",
           effects=[{"type": "aoe", "target": "enemy_minions", "amount": 1},
                    {"type": "draw", "target": "owner", "amount": 1}], hero="rogue"),
    _spell("assassinate_spell", "刺杀", 4, "消灭一个敌方随从。", targeting="enemy_minion",
           effects=[{"type": "destroy", "target": "chosen"}], hero="rogue"),
    _spell("shadow_step", "暗影步", 1, "使一个友方随从获得+2攻击力和风怒。",
           targeting="friendly_minion",
           effects=[{"type": "buff", "target": "chosen", "attack": 2, "health": 0},
                    {"type": "grant", "target": "chosen", "keyword": "windfury"}],
           hero="rogue", rarity="rare"),
    _minion("shadow_recruit", "暗影新兵", 1, 2, 1, "冲锋。", keywords=("charge",), hero="rogue"),
    _minion("poison_blade", "淬毒刺客", 3, 3, 2, "战吼：对一个敌方随从造成2点伤害。",
            targeting="enemy_minion",
            effects=[{"type": "damage", "target": "chosen", "amount": 2}], hero="rogue"),
    _minion("night_prowler", "夜行掠影", 4, 4, 3, "风怒。", keywords=("windfury",), hero="rogue",
            rarity="rare"),
    _minion("gadget_smuggler", "机巧走私客", 4, 3, 4, "战吼：抽两张牌。",
            effects=[{"type": "draw", "target": "owner", "amount": 2}], hero="rogue"),
    _minion("blade_flurry_m", "旋刃刺客", 5, 5, 4, "战吼：对所有敌方随从造成2点伤害。",
            effects=[{"type": "aoe", "target": "enemy_minions", "amount": 2}], hero="rogue",
            rarity="rare"),
    _minion("master_thief", "盗贼宗师", 6, 5, 5, "冲锋。风怒。",
            keywords=("charge", "windfury"), hero="rogue", rarity="epic"),
    _minion("shadow_sovereign", "暗影君王", 8, 7, 7, "冲锋。战吼：抽两张牌。",
            keywords=("charge",), hero="rogue", rarity="legendary",
            effects=[{"type": "draw", "target": "owner", "amount": 2}]),
]

EXTRA_TOKENS: dict[str, Card] = {
    "tomb_servant": _minion("tomb_servant", "墓仆", 2, 2, 2),
    "mirror_minion": _minion("mirror_minion", "镜像", 1, 1, 1, "嘲讽。", keywords=("taunt",)),
    "treant": _minion("treant", "树人", 2, 2, 2),
    "beast_2_2": _minion("beast_2_2", "猎场野兽", 2, 2, 2),
    "beast_3_3": _minion("beast_3_3", "荒野巨兽", 3, 3, 3),
    "beast_2_2_charge": _minion("beast_2_2_charge", "迅袭野兽", 2, 2, 2, "冲锋。",
                                keywords=("charge",)),
}
TOKENS: dict[str, Card] = {
    "sheep": _minion("sheep", "驯顺羔羊", 1, 1, 1),
    "hound": _minion("hound", "猎场恶犬", 1, 1, 1, "冲锋。", keywords=("charge",)),
    "hyena": _minion("hyena", "斑纹鬣兽", 2, 2, 2),
}
TOKENS.update(EXTRA_TOKENS)

CLASS_POOLS: dict[str, list[Card]] = {
    "mage": MAGE_CARDS + MAGE_EXTRA,
    "warrior": WARRIOR_CARDS + WARRIOR_EXTRA,
    "priest": PRIEST_CARDS + PRIEST_EXTRA,
    "hunter": HUNTER_CARDS + HUNTER_EXTRA,
    "druid": DRUID_CARDS,
    "rogue": ROGUE_CARDS,
}

NEUTRAL_POOL: list[Card] = NEUTRAL_CARDS + NEUTRAL_EXTRA

ALL_CARDS: dict[str, Card] = {}
for _c in NEUTRAL_POOL:
    ALL_CARDS[_c.cid] = _c
for _pool in CLASS_POOLS.values():
    for _c in _pool:
        ALL_CARDS[_c.cid] = _c
ALL_CARDS.update(TOKENS)

# 可收集卡牌（不含由效果生成的衍生物），用于图鉴与牌库编辑器
COLLECTIBLE: list[Card] = [c for cid, c in ALL_CARDS.items() if cid not in TOKENS]

DECK_SIZE = 30
MAX_COPIES = 2
MAX_LEGENDARY_COPIES = 1


def buildable_pool(hero_id: str) -> list[Card]:
    """某英雄可用于构筑的卡牌：本职业专属 + 全部中立。"""
    pool = list(CLASS_POOLS.get(hero_id, [])) + list(NEUTRAL_POOL)
    return sorted(pool, key=lambda c: (c.cost, c.hero != "neutral", c.name))


def max_copies_of(card: Card) -> int:
    return MAX_LEGENDARY_COPIES if card.rarity == "legendary" else MAX_COPIES


def validate_deck(hero_id: str, deck: list[str]) -> tuple[bool, str]:
    """校验套牌是否合法：30 张、无越界职业卡、单卡张数不超限。"""
    if len(deck) != DECK_SIZE:
        return False, f"套牌需要恰好 {DECK_SIZE} 张，当前 {len(deck)} 张。"
    allowed = {c.cid for c in buildable_pool(hero_id)}
    counts: dict[str, int] = {}
    for cid in deck:
        if cid not in ALL_CARDS:
            return False, f"存在未知卡牌：{cid}"
        if cid not in allowed:
            return False, f"{ALL_CARDS[cid].name} 不属于该英雄可用卡池。"
        counts[cid] = counts.get(cid, 0) + 1
    for cid, num in counts.items():
        card = ALL_CARDS[cid]
        limit = max_copies_of(card)
        if num > limit:
            kind = "传说" if card.rarity == "legendary" else "普通"
            return False, f"{card.name}（{kind}）最多 {limit} 张，当前 {num} 张。"
    return True, "套牌合法。"


def _deck(class_cards: list[str], neutrals: list[str]) -> list[str]:
    """每张牌两张，构成 30 张预组套牌。"""
    deck: list[str] = []
    for cid in class_cards + neutrals:
        deck.extend([cid, cid])
    return deck[:DECK_SIZE]

HEROES: dict[str, Hero] = {
    "mage": Hero(
        "mage", "塞拉菲娜·晨曜", "法师", "烈焰灼击", "造成1点伤害。", 2, "any_character",
        ({"type": "damage", "target": "chosen", "amount": 1},),
        _deck(["fireball", "frostbolt", "arcane_missiles", "flamestrike", "polymorph",
               "water_elemental", "arcane_intellect", "arcane_bolt", "frost_nova",
               "pyromancer", "sorcerer_app"],
              ["elven_archer", "bloodfen_raptor", "chillwind_yeti", "sen_jin"]),
    ),
    "warrior": Hero(
        "warrior", "格洛姆·裂颅", "战士", "披甲备战", "获得2点护甲。", 2, "none",
        ({"type": "armor", "target": "owner", "amount": 2},),
        _deck(["shield_block", "execute", "whirlwind", "charge_spell", "armorsmith",
               "frothing_berserk", "kor_elite", "battle_shout", "cleave", "iron_captain",
               "shield_maiden"],
              ["frostwolf_grunt", "ironfur_grizzly", "chillwind_yeti", "war_golem"]),
    ),
    "priest": Hero(
        "priest", "艾德林·圣言", "牧师", "抚慰之光", "恢复2点生命。", 2, "any_character",
        ({"type": "heal", "target": "chosen", "amount": 2},),
        _deck(["holy_smite", "power_word_shield", "shadow_word_pain", "holy_nova",
               "northshire_cleric", "temple_enforcer", "mind_blast", "healing_rain",
               "light_whelp", "holy_avenger", "ivory_priest"],
              ["argent_squire", "river_croc", "chillwind_yeti", "sen_jin"]),
    ),
    "hunter": Hero(
        "hunter", "卡兰·荒踪", "猎人", "精准狙击", "对敌方英雄造成2点伤害。", 2, "none",
        ({"type": "damage", "target": "enemy_hero", "amount": 2},),
        _deck(["arcane_shot", "kill_command", "multi_shot", "unleash", "houndmaster",
               "savannah_highmane", "timber_wolf", "rapid_shot", "eagle_eye", "alpha_wolf",
               "pack_leader"],
              ["murloc_raider", "bloodfen_raptor", "wolfrider", "chillwind_yeti"]),
    ),
    "druid": Hero(
        "druid", "薇兰德·叶语", "德鲁伊", "变形之力", "获得1点护甲并造成1点伤害。", 2,
        "any_character",
        ({"type": "armor", "target": "owner", "amount": 1},
         {"type": "damage", "target": "chosen", "amount": 1}),
        _deck(["wild_growth", "claw_swipe", "nourish", "mark_of_wild", "starfall", "moonfire",
               "sapling", "grove_keeper", "bear_form", "thorn_beast", "ancient_protector"],
              ["river_croc", "ironfur_grizzly", "chillwind_yeti", "verdant_ancient"]),
    ),
    "rogue": Hero(
        "rogue", "希兰·影刃", "盗贼", "淬毒之刃", "对敌方随从造成1点伤害并抽一张牌。", 2,
        "enemy_minion",
        ({"type": "damage", "target": "chosen", "amount": 1},
         {"type": "draw", "target": "owner", "amount": 1}),
        _deck(["backstab", "eviscerate", "fan_of_knives", "assassinate_spell", "shadow_step",
               "shadow_recruit", "poison_blade", "night_prowler", "gadget_smuggler",
               "blade_flurry_m", "master_thief"],
              ["murloc_raider", "bloodfen_raptor", "dusk_stalker", "chillwind_yeti"]),
    ),
}


def get_card(cid: str) -> Card:
    return ALL_CARDS[cid]