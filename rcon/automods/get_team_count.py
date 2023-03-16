from typing import Literal


def get_team_count(team_view, team: Literal["axis", "allies"]):
    if team not in team_view:
        return 0

    return sum(
        len(s.get("players", [])) for s in team_view[team].get("squads", {}).values()
    ) + len(team_view[team].get("commander", {}))
