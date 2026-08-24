"""无界面自检：让两个 AI 互相对战，验证规则引擎稳定性。"""

from __future__ import annotations

import itertools
import sys

from .ai import SimpleAI
from .cards import HEROES
from .engine import Game


def play_one(hero_a: str, hero_b: str, seed: int, max_turns: int = 120) -> tuple[int | None, int]:
    game = Game(hero_a, hero_b, ai_second=True, seed=seed)
    turns = 0
    while not game.finished and turns < max_turns:
        SimpleAI(game, game.me).take_turn()
        if game.finished:
            break
        game.end_turn()
        turns += 1
    return game.winner, turns


def main(rounds: int = 3) -> int:
    results: dict[str, int] = {}
    total = 0
    for hero_a, hero_b in itertools.permutations(HEROES, 2):
        for seed in range(rounds):
            winner, turns = play_one(hero_a, hero_b, seed)
            total += 1
            key = "平局" if winner is None else (hero_a if winner == 0 else hero_b)
            results[key] = results.get(key, 0) + 1
            if turns >= 120:
                print(f"警告：{hero_a} vs {hero_b} seed={seed} 未在限定回合内结束")
    print(f"完成 {total} 局模拟对战，胜场统计：{results}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
