from rcon.game_logs import on_match_end
from rcon.types import CachedLiveGameStats, GetDetailedPlayers
from rcon.user_config.end_of_round_rewards import (
    EndOfRoundRewardsUserConfig,
    ALLOWED_VARIABLES,
    RoleReward,
)
from rcon.types import Roles

from rcon.scoreboard import get_cached_live_game_stats
from rcon.api_commands import get_rcon_api
from collections import defaultdict, Counter
from logging import getLogger
from pprint import pprint

logger = getLogger(__name__)


@on_match_end
def reward_players():
    config = EndOfRoundRewardsUserConfig.load_from_db()
    api = get_rcon_api()

    role_reward = RoleReward(roles=[Roles.squad_lead], formula="support * 2 + kills")
    config.role_rewards = [role_reward]
    config.enabled = True

    reward_lookup: dict[int, RoleReward] = {
        idx: reward for idx, reward in enumerate(config.role_rewards)
    }

    if config.enabled:
        stats: CachedLiveGameStats = get_cached_live_game_stats()
        players: GetDetailedPlayers = api.get_detailed_players()

        # logger.info(f"{stats.keys()=}")
        # print(f"{stats.keys()=}")

        # logger.info(f"{stats['stats']=}")
        # print(f"{stats['stats']=}")

        formulas: defaultdict[int, list[tuple[str, str]]] = defaultdict(list)
        # Iterate over all the players first, then check which conditions they meet
        # since we likely have far more players than conditions
        for stat in stats["stats"]:
            player_id = stat["player_id"]
            for idx, role_reward in enumerate(config.role_rewards):
                try:
                    if players["players"][player_id]["role"] in role_reward.roles:
                        subbed = role_reward.substituable_formula.format_map(stat)
                        formulas[idx].append((player_id, subbed))
                    else:
                        print(f"{player_id} not in {role_reward.roles}")
                except KeyError as e:
                    print(f"skipping {player_id}: {e} not online")
                    continue

        print(f"Formulas=")
        pprint(formulas)

        calculated_formulas: dict[int, Counter] = dict()
        for idx, rewards in formulas.items():
            calculated_formulas[idx] = Counter(
                {player_id: eval(f) for player_id, f in rewards}
            )

        print(f"Calculated formulas=")
        pprint(calculated_formulas)

        for idx in calculated_formulas.keys():
            top_n = reward_lookup[idx].top_n
            print(f"{top_n=} {calculated_formulas[idx].most_common(top_n)}")


if __name__ == "__main__":
    reward_players()
