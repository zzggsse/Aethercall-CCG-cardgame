"""对战规则引擎：法力、抽牌、随从战斗、法术效果与胜负判定。"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .cards import HEROES, Card, Hero, get_card

MAX_BOARD = 7
MAX_HAND = 10
MAX_MANA = 10
START_HEALTH = 30
FATIGUE_START = 1


@dataclass
class Minion:
    """场上的随从实体。"""

    card: Card
    owner: int
    uid: int
    attack: int
    max_health: int
    health: int
    keywords: set[str] = field(default_factory=set)
    can_attack: bool = False
    attacks_left: int = 0
    frozen: bool = False
    divine_shield: bool = False
    dead: bool = False
    silenced: bool = False

    @property
    def name(self) -> str:
        return self.card.name

    @property
    def is_hero(self) -> bool:
        return False

    @property
    def taunt(self) -> bool:
        return "taunt" in self.keywords

    def buffed_attack(self, aura: int) -> int:
        return max(0, self.attack + aura)


@dataclass
class HeroEntity:
    """英雄实体（玩家的可攻击目标）。"""

    hero: Hero
    owner: int
    health: int = START_HEALTH
    max_health: int = START_HEALTH
    armor: int = 0
    frozen: bool = False
    divine_shield: bool = False

    @property
    def name(self) -> str:
        return self.hero.name

    @property
    def is_hero(self) -> bool:
        return True


@dataclass
class Player:
    """一名玩家的完整状态。"""

    index: int
    hero_entity: HeroEntity
    deck: list[Card]
    hand: list[Card] = field(default_factory=list)
    board: list[Minion] = field(default_factory=list)
    mana: int = 0
    max_mana: int = 0
    fatigue: int = 0
    power_used: bool = False
    is_ai: bool = False
    overdrawn: int = 0
    traps: list[str] = field(default_factory=list)
    spells_cast: int = 0

    @property
    def name(self) -> str:
        return self.hero_entity.hero.name

    @property
    def class_name(self) -> str:
        return self.hero_entity.hero.class_name


class Game:
    """一局对战的状态机。"""

    def __init__(self, hero_a: str, hero_b: str, ai_second: bool = True,
                 seed: int | None = None, deck_a: list[str] | None = None,
                 deck_b: list[str] | None = None) -> None:
        self.rng = random.Random(seed)
        self._uid = 0
        self.log: list[str] = []
        self.turn = 0
        self.winner: int | None = None
        self.finished = False
        self.players = [
            self._make_player(0, hero_a, False, deck_a),
            self._make_player(1, hero_b, ai_second, deck_b),
        ]
        self.current = 0
        self._opening_draw()
        self.begin_turn(first=True)

    # ---------- 初始化 ----------

    def _make_player(self, index: int, hero_id: str, is_ai: bool,
                     deck_list: list[str] | None = None) -> Player:
        hero = HEROES[hero_id]
        deck = [get_card(cid) for cid in (deck_list or hero.deck)]
        self.rng.shuffle(deck)
        return Player(index, HeroEntity(hero, index), deck, is_ai=is_ai)

    def _opening_draw(self) -> None:
        for _ in range(3):
            self.draw(self.players[0])
        for _ in range(4):
            self.draw(self.players[1])

    def next_uid(self) -> int:
        self._uid += 1
        return self._uid

    # ---------- 查询辅助 ----------

    @property
    def me(self) -> Player:
        return self.players[self.current]

    @property
    def foe(self) -> Player:
        return self.players[1 - self.current]

    def opponent_of(self, player: Player) -> Player:
        return self.players[1 - player.index]

    def aura_attack(self, minion: Minion) -> int:
        """计算光环提供的攻击力加成。"""
        owner = self.players[minion.owner]
        bonus = 0
        for other in owner.board:
            if other is minion or other.dead:
                continue
            if "aura_attack" in other.keywords:
                bonus += 1
        return bonus

    def display_attack(self, minion: Minion) -> int:
        return minion.buffed_attack(self.aura_attack(minion))

    def can_be_attacked(self, defender: Minion | HeroEntity) -> bool:
        """嘲讽保护判定。"""
        owner = self.players[defender.owner]
        taunts = [m for m in owner.board if m.taunt and not m.dead]
        if not taunts:
            return True
        return (not defender.is_hero) and defender in taunts

    def minion_can_attack(self, minion: Minion) -> bool:
        return (not minion.dead and not minion.frozen and minion.attacks_left > 0
                and self.display_attack(minion) > 0)

    def playable_cards(self, player: Player) -> list[Card]:
        return [c for c in player.hand if self.can_play(player, c)]

    def effective_cost(self, player: Player, card: Card) -> int:
        """实际消耗，考虑法术折扣与「本局法术数」折扣。"""
        cost = card.cost
        if card.is_spell:
            discount = sum(1 for m in player.board
                           if not m.dead and "spell_cost_down" in m.keywords)
            if discount:
                cost = max(1, cost - discount)
        if "arcane_cost" in card.keywords:
            cost = max(1, cost - player.spells_cast)
        return max(0, cost)

    def spell_power(self, player: Player) -> int:
        """法术强度加成。"""
        return sum(1 for m in player.board if not m.dead and "spell_power" in m.keywords)

    def can_play(self, player: Player, card: Card) -> bool:
        if self.effective_cost(player, card) > player.mana:
            return False
        if card.is_minion and len(player.board) >= MAX_BOARD:
            return False
        if card.targeting != "none" and not self.valid_targets(player, card.targeting):
            return False
        return True

    def can_use_power(self, player: Player) -> bool:
        hero = player.hero_entity.hero
        if player.power_used or player.mana < hero.power_cost:
            return False
        if hero.power_targeting != "none" and not self.valid_targets(player, hero.power_targeting):
            return False
        return True

    def valid_targets(self, player: Player, mode: str) -> list[Minion | HeroEntity]:
        """按目标模式列出合法目标。"""
        foe = self.opponent_of(player)
        mine = [m for m in player.board if not m.dead]
        theirs = [m for m in foe.board if not m.dead]
        if mode == "none":
            return []
        if mode == "any_character":
            return [*mine, *theirs, player.hero_entity, foe.hero_entity]
        if mode == "any_minion":
            return [*mine, *theirs]
        if mode == "friendly_minion":
            return mine
        if mode == "enemy_minion":
            return theirs
        if mode == "damaged_enemy_minion":
            return [m for m in theirs if m.health < m.max_health]
        if mode == "strong_minion":
            return [m for m in [*mine, *theirs] if self.display_attack(m) >= 5]
        if mode == "undamaged_minion":
            return [m for m in [*mine, *theirs] if m.health >= m.max_health]
        if mode == "weak_minion":
            return [m for m in [*mine, *theirs] if self.display_attack(m) <= 3]
        return []

    # ---------- 回合流程 ----------

    def begin_turn(self, first: bool = False) -> None:
        player = self.me
        self.turn += 1
        player.max_mana = min(MAX_MANA, player.max_mana + 1)
        player.mana = player.max_mana
        player.power_used = False
        for minion in player.board:
            minion.frozen = False
            minion.attacks_left = 2 if "windfury" in minion.keywords else 1
            minion.can_attack = True
        self.draw(player)
        self.logline(f"—— 第{(self.turn + 1) // 2}回合：{player.name}（{player.class_name}）行动 ——")

    def end_turn(self) -> None:
        if self.finished:
            return
        for minion in self.me.board:
            minion.can_attack = False
        self.current = 1 - self.current
        self.begin_turn()
        self.check_state()

    def draw(self, player: Player) -> None:
        if not player.deck:
            player.fatigue += FATIGUE_START
            self.logline(f"{player.name} 牌库已空，受到 {player.fatigue} 点疲劳伤害。")
            self.damage_character(player.hero_entity, player.fatigue, source_name="疲劳")
            return
        card = player.deck.pop()
        if len(player.hand) >= MAX_HAND:
            player.overdrawn += 1
            self.logline(f"{player.name} 手牌已满，{card.name} 被烧掉。")
            return
        player.hand.append(card)

    # ---------- 行动 ----------

    def play_card(self, player: Player, card: Card,
                  target: Minion | HeroEntity | None = None,
                  position: int | None = None) -> bool:
        if self.finished or player.index != self.current:
            return False
        if card not in player.hand or not self.can_play(player, card):
            return False
        if card.targeting != "none":
            if target is None or target not in self.valid_targets(player, card.targeting):
                return False
        player.hand.remove(card)
        player.mana -= self.effective_cost(player, card)
        if card.is_minion:
            minion = self.summon(player, card, position)
            self.logline(f"{player.name} 打出随从 {card.name}（{minion.attack}/{minion.health}）。")
            self.resolve_effects(player, card.effects, target, source=minion)
        else:
            player.spells_cast += 1
            self.logline(f"{player.name} 施放法术 {card.name}。")
            self.resolve_effects(player, card.effects, target, source=None)
        self.cleanup()
        self.check_state()
        return True

    def summon(self, player: Player, card: Card, position: int | None = None) -> Minion:
        minion = Minion(
            card=card, owner=player.index, uid=self.next_uid(),
            attack=card.attack, max_health=card.health, health=card.health,
            keywords=set(card.keywords),
        )
        minion.divine_shield = "divine_shield" in minion.keywords
        if any("aura_charge" in o.keywords for o in player.board
               if o is not minion and not o.dead):
            minion.keywords.add("charge")
        if "charge" in minion.keywords:
            minion.attacks_left = 1
            minion.can_attack = True
        if "aura_health" in minion.keywords:
            for other in player.board:
                if not other.dead:
                    other.max_health += 1
                    other.health += 1
        if position is None or not (0 <= position <= len(player.board)):
            player.board.append(minion)
        else:
            player.board.insert(position, minion)
        return minion

    def use_hero_power(self, player: Player, target: Minion | HeroEntity | None = None) -> bool:
        if self.finished or player.index != self.current or not self.can_use_power(player):
            return False
        hero = player.hero_entity.hero
        if hero.power_targeting != "none":
            if target is None or target not in self.valid_targets(player, hero.power_targeting):
                return False
        player.mana -= hero.power_cost
        player.power_used = True
        self.logline(f"{player.name} 使用英雄技能 {hero.power_name}。")
        self.resolve_effects(player, hero.power_effects, target, source=None)
        self.cleanup()
        self.check_state()
        return True

    def attack(self, attacker: Minion, defender: Minion | HeroEntity) -> bool:
        if self.finished or attacker.owner != self.current:
            return False
        if not self.minion_can_attack(attacker) or not self.can_be_attacked(defender):
            return False
        if defender.owner == attacker.owner:
            return False
        attacker.attacks_left -= 1
        atk = self.display_attack(attacker)
        def_atk = 0 if defender.is_hero else self.display_attack(defender)
        self.logline(f"{attacker.name} 攻击 {defender.name}。")
        if defender.is_hero:
            self._trigger_traps(self.players[defender.owner])
        self.damage_character(defender, atk, source_name=attacker.name, source=attacker)
        if def_atk > 0:
            self.damage_character(attacker, def_atk, source_name=defender.name, source=defender)
        if not defender.is_hero and "freeze_attacker" in defender.keywords:
            attacker.frozen = True
        if "freeze_attacker" in attacker.keywords and not defender.is_hero:
            defender.frozen = True
        self.cleanup()
        self.check_state()
        return True

    def _trigger_traps(self, owner: Player) -> None:
        """英雄被攻击时触发已布置的陷阱。"""
        for trap in list(owner.traps):
            if trap == "explosive":
                owner.traps.remove(trap)
                self.logline(f"{owner.name} 的爆炸陷阱触发！")
                foe = self.opponent_of(owner)
                for minion in list(foe.board):
                    if not minion.dead:
                        self.damage_character(minion, 2, source_name="爆炸陷阱")
                self.cleanup()

    # ---------- 效果解析 ----------

    def resolve_effects(self, player: Player, effects, chosen, source: Minion | None) -> None:
        for effect in effects:
            self.apply_effect(player, effect, chosen, source)

    def _resolve_target(self, player: Player, spec: str, chosen):
        foe = self.opponent_of(player)
        if spec == "chosen":
            return [chosen] if chosen is not None else []
        if spec == "owner":
            return [player.hero_entity]
        if spec == "enemy_hero":
            return [foe.hero_entity]
        if spec == "enemy_minions":
            return [m for m in foe.board if not m.dead]
        if spec == "friendly_minions":
            return [m for m in player.board if not m.dead]
        if spec == "all_minions":
            return [m for m in player.board + foe.board if not m.dead]
        if spec == "enemy_characters":
            return [*[m for m in foe.board if not m.dead], foe.hero_entity]
        if spec == "friendly_characters":
            return [*[m for m in player.board if not m.dead], player.hero_entity]
        if spec == "all_characters":
            return [*[m for m in player.board + foe.board if not m.dead],
                    player.hero_entity, foe.hero_entity]
        return []

    def apply_effect(self, player: Player, effect: dict, chosen, source: Minion | None) -> None:
        kind = effect["type"]
        if kind == "damage":
            bonus = self.spell_power(player)
            for target in self._resolve_target(player, effect["target"], chosen):
                self.damage_character(target, effect["amount"] + bonus, source_name="法术")
        elif kind == "aoe":
            for target in list(self._resolve_target(player, effect["target"], chosen)):
                self.damage_character(target, effect["amount"], source_name="范围效果")
        elif kind == "heal":
            for target in self._resolve_target(player, effect["target"], chosen):
                self.heal_character(target, effect["amount"])
        elif kind == "mass_heal":
            for target in self._resolve_target(player, effect["target"], chosen):
                self.heal_character(target, effect["amount"])
        elif kind == "draw":
            for _ in range(effect["amount"]):
                self.draw(player)
        elif kind == "armor":
            player.hero_entity.armor += effect["amount"]
            self.logline(f"{player.name} 获得 {effect['amount']} 点护甲。")
        elif kind == "buff":
            for target in self._resolve_target(player, effect["target"], chosen):
                if target.is_hero:
                    continue
                target.attack += effect.get("attack", 0)
                gain = effect.get("health", 0)
                target.max_health += gain
                target.health += gain
        elif kind == "grant":
            for target in self._resolve_target(player, effect["target"], chosen):
                if not target.is_hero:
                    target.keywords.add(effect["keyword"])
                    if effect["keyword"] == "charge":
                        target.attacks_left = max(target.attacks_left, 1)
        elif kind == "freeze":
            for target in self._resolve_target(player, effect["target"], chosen):
                target.frozen = True
        elif kind == "destroy":
            for target in self._resolve_target(player, effect["target"], chosen):
                if not target.is_hero:
                    target.health = 0
                    self.logline(f"{target.name} 被消灭。")
        elif kind == "polymorph":
            for target in self._resolve_target(player, effect["target"], chosen):
                if target.is_hero:
                    continue
                owner = self.players[target.owner]
                if target in owner.board:
                    index = owner.board.index(target)
                    owner.board.pop(index)
                    self.logline(f"{target.name} 变成了羔羊。")
                    self.summon(owner, get_card("sheep"), index)
        elif kind == "random_damage":
            pool = self._resolve_target(player, effect["target"], chosen)
            for _ in range(effect["amount"]):
                pool = [t for t in pool if t.is_hero or not t.dead]
                if not pool:
                    break
                self.damage_character(self.rng.choice(pool), 1, source_name="随机伤害")
        elif kind == "random_split":
            for _ in range(effect.get("times", 1)):
                pool = [t for t in self._resolve_target(player, effect["target"], chosen)
                        if t.is_hero or not t.dead]
                if not pool:
                    break
                self.damage_character(self.rng.choice(pool), effect["amount"],
                                      source_name="随机伤害")
        elif kind == "summon":
            for _ in range(effect.get("count", 1)):
                if len(player.board) >= MAX_BOARD:
                    break
                token = self.summon(player, get_card(effect["token"]))
                self.logline(f"{player.name} 召唤了 {token.name}。")
        elif kind == "summon_per_enemy":
            enemies = len([m for m in self.opponent_of(player).board if not m.dead])
            for _ in range(enemies):
                if len(player.board) >= MAX_BOARD:
                    break
                token = self.summon(player, get_card(effect["token"]))
                self.logline(f"{player.name} 召唤了 {token.name}。")
        elif kind == "give_mana":
            gain = effect.get("amount", 1)
            player.max_mana = min(MAX_MANA, player.max_mana + gain)
            player.mana = min(player.max_mana, player.mana + gain)
            self.logline(f"{player.name} 获得 {gain} 个法力水晶。")
        elif kind == "silence":
            for target in self._resolve_target(player, effect["target"], chosen):
                if not target.is_hero:
                    self.silence_minion(target)
        elif kind == "set_attack_to_health":
            for target in self._resolve_target(player, effect["target"], chosen):
                if not target.is_hero:
                    target.attack = target.health
                    self.logline(f"{target.name} 的攻击力变为 {target.attack}。")
        elif kind == "double_health":
            for target in self._resolve_target(player, effect["target"], chosen):
                if not target.is_hero:
                    target.max_health += target.health
                    target.health *= 2
                    self.logline(f"{target.name} 的生命值翻倍至 {target.health}。")
        elif kind == "random_buff":
            pool = [m for m in self._resolve_target(player, effect["target"], chosen)
                    if not m.is_hero and not m.dead]
            if pool:
                target = self.rng.choice(pool)
                target.attack += effect.get("attack", 0)
                gain = effect.get("health", 0)
                target.max_health += gain
                target.health += gain
                self.logline(f"{target.name} 获得强化。")
        elif kind == "armor_damage":
            amount = player.hero_entity.armor
            for target in self._resolve_target(player, effect["target"], chosen):
                self.damage_character(target, amount, source_name="盾击")
        elif kind == "conditional_damage":
            base = effect["amount"]
            for target in self._resolve_target(player, effect["target"], chosen):
                final = base
                if effect.get("if_frozen") and getattr(target, "frozen", False):
                    final = effect["if_frozen"]
                below = effect.get("if_hero_below")
                if below and player.hero_entity.health <= below:
                    final = effect.get("then", base)
                self.damage_character(target, final, source_name="法术")
        elif kind == "mark":
            for target in self._resolve_target(player, effect["target"], chosen):
                if not target.is_hero:
                    target.keywords.add("marked")
                    self.logline(f"{target.name} 被标记。")
        elif kind == "trap_explosive":
            player.traps.append("explosive")
            self.logline(f"{player.name} 布置了一个陷阱。")
        elif kind == "add_random_class_spells":
            from .cards import CLASS_POOLS
            pool = [c for c in CLASS_POOLS.get(effect.get("hero", ""), []) if c.is_spell]
            for _ in range(effect.get("count", 1)):
                if not pool or len(player.hand) >= MAX_HAND:
                    break
                card = self.rng.choice(pool)
                player.hand.append(card)
                self.logline(f"{player.name} 获得了 {card.name}。")

    def silence_minion(self, minion: Minion) -> None:
        """沉默：移除关键词、光环与亡语。"""
        if "aura_health" in minion.keywords:
            owner = self.players[minion.owner]
            for other in owner.board:
                if other is not minion and not other.dead:
                    other.max_health = max(1, other.max_health - 1)
                    other.health = min(other.health, other.max_health)
        minion.keywords.clear()
        minion.divine_shield = False
        minion.silenced = True
        self.logline(f"{minion.name} 被沉默。")

    # ---------- 伤害与治疗 ----------

    def damage_character(self, target, amount: int, source_name: str = "",
                         source: Minion | None = None) -> None:
        if amount <= 0:
            return
        if getattr(target, "divine_shield", False):
            target.divine_shield = False
            if not target.is_hero:
                target.keywords.discard("divine_shield")
            self.logline(f"{target.name} 的圣盾被打破。")
            return
        if target.is_hero:
            absorbed = min(target.armor, amount)
            target.armor -= absorbed
            target.health -= amount - absorbed
            self.logline(f"{target.name} 受到 {amount} 点伤害（剩余 {max(0, target.health)} 点生命）。")
        else:
            target.health -= amount
            self.logline(f"{target.name} 受到 {amount} 点伤害。")
            self._on_minion_damaged(target)

    def _on_minion_damaged(self, target: Minion) -> None:
        if "marked" in target.keywords:
            target.health = 0
        for player in self.players:
            for minion in player.board:
                if minion.dead:
                    continue
                if "frothing" in minion.keywords:
                    minion.attack += 1
                if "armorsmith" in minion.keywords and target.owner == minion.owner:
                    player.hero_entity.armor += 1

    def heal_character(self, target, amount: int) -> None:
        if target.is_hero:
            before = target.health
            target.health = min(target.max_health, target.health + amount)
            healed = target.health - before
        else:
            before = target.health
            target.health = min(target.max_health, target.health + amount)
            healed = target.health - before
        if healed > 0:
            self.logline(f"{target.name} 恢复了 {healed} 点生命。")
            for player in self.players:
                for minion in player.board:
                    if "cleric" in minion.keywords and not minion.dead:
                        self.draw(self.players[minion.owner])

    # ---------- 死亡结算 ----------

    def cleanup(self) -> None:
        for _ in range(8):
            dying: list[tuple[Player, Minion]] = []
            for player in self.players:
                for minion in player.board:
                    if minion.health <= 0 and not minion.dead:
                        minion.dead = True
                        dying.append((player, minion))
            if not dying:
                break
            for player, minion in dying:
                if minion in player.board:
                    player.board.remove(minion)
                self.logline(f"{minion.name} 死亡。")
                if "aura_health" in minion.keywords:
                    for other in player.board:
                        other.max_health = max(1, other.max_health - 1)
                        other.health = min(other.health, other.max_health)
                if minion.card.deathrattle and not minion.silenced:
                    self.resolve_effects(player, minion.card.deathrattle, None, None)

    def check_state(self) -> None:
        dead = [p for p in self.players if p.hero_entity.health <= 0]
        if not dead:
            return
        self.finished = True
        if len(dead) == 2:
            self.winner = None
            self.logline("双方英雄同时倒下，平局！")
        else:
            loser = dead[0]
            self.winner = 1 - loser.index
            self.logline(f"{self.players[self.winner].name} 获得胜利！")

    def logline(self, text: str) -> None:
        self.log.append(text)
        if len(self.log) > 400:
            del self.log[:100]
