def get_team_count(team_view, team):
    if team_view[team] is None:
        return 0
    return sum(
        len(s.get("players", [])) for s in team_view[team].get("squads", {}).values()
    )
