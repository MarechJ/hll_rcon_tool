def _get_team_count(team_view, team):
    return sum(
        len(s.get("players", [])) for s in team_view[team].get("squads", {}).values()
    )
