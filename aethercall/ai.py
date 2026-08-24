"""AI 对手：基于启发式评分的贪心决策。"""

from __future__ import annotations

from .engine import Game, HeroEntity, Minion, Player


class SimpleAI:
    """会打牌、用技能、按价值换血并寻找斩杀线的对手。"""

    def __init__(self, game: Game, player: Player) -> None:
        self.game = game
        self.player = player

    # ---------- 主循环 ----------

    def take_turn(self, max_actions: int = 60) -> list[str]:
        actions: list[str] = []
        for _ in range(max_actions):
            if self.game.finished or self.game.current != self.player.index:
                break
            if self._try_lethal():
                actions.append("lethal")
                continue
            if self._play_best_card():
                actions.append("play")
                continue
            if self._use_power():
                actions.append("power")
                continue
            if self._attack_once():
                actions.append("attack")
                continue
            break
        return actions

    # ---------- 斩杀检查 ----------

    def _try_lethal(self) -> bool:
        game, me = self.game, self.player
        foe = game.opponent_of(me)
        if [m for m in foe.board if m.taunt and not m.dead]:
            return False
        total = sum(game.display_attack(m) for m in me.board if game.minion_can_attack(m))
        if total < foe.hero_entity.health + foe.hero_entity.armor:
            return False
        for minion in list(me.board):
            if game.minion_can_attack(minion):
                return game.attack(minion, foe.hero_entity)
        return False

    # ---------- 出牌 ----------

    def _play_best_card(self) -> bool:
        game, me = self.game, self.player
        best = None
        best_score = 0.0
        for card in list(me.hand):
            if not game.can_play(me, card):
                continue
            targets = game.valid_targets(me, card.targeting) or [None]
            for target in targets:
                score = self._score_play(card, target)
                if score > best_score:
                    best, best_score = (card, target), score
        if best is None:
            return False
        card, target = best
        return game.play_card(me, card, target)

    def _score_play(self, card, target) -> float:
        game, me = self.game, self.player
        foe = game.opponent_of(me)
        score = 1.0 + card.cost * 0.6
        if card.is_minion:
            score += card.attack * 0.7 + card.health * 0.6
            if "taunt" in card.keywords:
                score += 1.0
            if "charge" in card.keywords:
                score += 1.0
            if "divine_shield" in card.keywords:
                score += 1.0
        for effect in card.effects:
            score += self._score_effect(effect, target, foe)
        if target is not None and not target.is_hero:
            damage = self._effect_damage(card.effects)
            if target.owner == me.index and damage:
                return 0.0
            if target.owner != me.index and damage:
                if damage >= target.health:
                    score += 3.0 + game.display_attack(target) * 0.8
                else:
                    score -= 1.0
            if target.owner != me.index and self._is_buff(card.effects):
                return 0.0
            if target.owner == me.index and self._is_buff(card.effects):
                score += 1.5
        if target is not None and target.is_hero:
            damage = self._effect_damage(card.effects)
            if target.owner == me.index and damage:
                return 0.0
            if target.owner != me.index and damage:
                score += 1.5 if damage < target.health else 12.0
        return score

    def _score_effect(self, effect: dict, target, foe: Player) -> float:
        kind = effect["type"]
        if kind == "draw":
            return 1.5 * effect.get("amount", 1)
        if kind == "armor":
            return 0.6 * effect.get("amount", 1)
        if kind in {"aoe", "random_damage", "random_split"}:
            hits = len([m for m in foe.board if not m.dead])
            return hits * 1.6
        if kind == "destroy":
            return 4.0
        if kind == "polymorph":
            return 3.0 if target is not None and target.owner != self.player.index else -5.0
        if kind == "summon" or kind == "summon_per_enemy":
            return 2.0
        if kind == "freeze":
            return 0.8
        return 0.0

    @staticmethod
    def _effect_damage(effects) -> int:
        return sum(e.get("amount", 0) for e in effects
                   if e["type"] in {"damage", "aoe"} and e.get("target") in
                   {"chosen", "enemy_hero"})

    @staticmethod
    def _is_buff(effects) -> bool:
        return any(e["type"] in {"buff", "grant", "heal"} for e in effects)

    # ---------- 英雄技能 ----------

    def _use_power(self) -> bool:
        game, me = self.game, self.player
        if not game.can_use_power(me):
            return False
        if me.mana > me.hero_entity.hero.power_cost and game.playable_cards(me):
            return False
        mode = me.hero_entity.hero.power_targeting
        if mode == "none":
            return game.use_hero_power(me)
        foe = game.opponent_of(me)
        effects = me.hero_entity.hero.power_effects
        healing = any(e["type"] == "heal" for e in effects)
        if healing:
            hurt = [m for m in me.board if m.health < m.max_health and not m.dead]
            if hurt:
                return game.use_hero_power(me, max(hurt, key=lambda m: m.max_health - m.health))
            hero = me.hero_entity
            if hero.health < hero.max_health - 1:
                return game.use_hero_power(me, hero)
            return False
        killable = [m for m in foe.board if not m.dead and m.health == 1]
        if killable:
            return game.use_hero_power(me, killable[0])
        return game.use_hero_power(me, foe.hero_entity)

    # ---------- 攻击 ----------

    def _attack_once(self) -> bool:
        game, me = self.game, self.player
        foe = game.opponent_of(me)
        for attacker in me.board:
            if not game.minion_can_attack(attacker):
                continue
            target = self._pick_target(attacker, foe)
            if target is not None:
                return game.attack(attacker, target)
        return False

    def _pick_target(self, attacker: Minion, foe: Player):
        game = self.game
        options = [m for m in foe.board if not m.dead]
        best, best_score = None, -99.0
        atk = game.display_attack(attacker)
        for minion in options:
            if not game.can_be_attacked(minion):
                continue
            enemy_atk = game.display_attack(minion)
            score = 0.0
            if atk >= minion.health:
                score += 3.0 + enemy_atk * 1.2
            else:
                score += enemy_atk * 0.4 - 1.0
            if enemy_atk >= attacker.health:
                score -= 2.0 + attacker.health * 0.3
            if minion.taunt:
                score += 0.5
            if score > best_score:
                best, best_score = minion, score
        hero: HeroEntity = foe.hero_entity
        if game.can_be_attacked(hero):
            hero_score = 2.0 + atk * 0.5
            if hero_score > best_score:
                return hero
        return best
