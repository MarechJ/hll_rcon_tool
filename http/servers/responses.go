package servers

import (
	"github.com/MarechJ/hll_rcon_tool/resources"
	"github.com/floriansw/go-hll-rcon/rconv2/api"
)

func renderServerList(sl []resources.Server) map[string]interface{} {
	servers := make([]map[string]interface{}, len(sl))
	for _, s := range sl {
		servers = append(servers, renderServer(s, false))
	}
	return map[string]interface{}{
		"servers": servers,
	}
}

func renderServer(s resources.Server, includeConnectionDetails bool) map[string]interface{} {
	r := map[string]interface{}{
		"id":    s.Id,
		"name":  s.Name,
		"state": s.State,
	}
	if s.ConnectionDetails != nil && includeConnectionDetails {
		r["connection_details"] = map[string]interface{}{
			"host":     s.ConnectionDetails.Host,
			"port":     s.ConnectionDetails.Port,
			"password": s.ConnectionDetails.Password,
		}
	}
	return r
}

func renderGameState(si *api.GetSessionResponse) map[string]interface{} {
	return map[string]interface{}{
		"server_name":         si.ServerName,
		"map_name":            si.MapName,
		"game_mode":           si.GameMode,
		"max_player_count":    si.MaxPlayerCount,
		"player_count":        si.PlayerCount,
		"max_queue_count":     si.MaxQueueCount,
		"queue_count":         si.QueueCount,
		"max_vip_queue_count": si.MaxVIPQueueCount,
		"vip_queue_count":     si.VIPQueueCount,
	}
}

func renderPlayerList(p *api.GetPlayersResponse) map[string]interface{} {
	players := make([]map[string]interface{}, len(p.Players))
	for _, player := range p.Players {
		players = append(players, renderPlayer(player))
	}
	return map[string]interface{}{
		"players": players,
	}
}

func renderPlayer(p api.GetPlayerResponse) map[string]interface{} {
	return map[string]interface{}{
		"id":       p.Id,
		"name":     p.Name,
		"platform": p.Platform,
		"team":     p.Team,
		"clan_tag": p.ClanTag,
		"level":    p.Level,
		"role":     p.Role,
		"squad":    p.Squad,
		"loadout":  p.Loadout,
		"score":    renderPlayerScore(p),
		"position": renderPlayerPosition(p),
	}
}

func renderPlayerScore(p api.GetPlayerResponse) map[string]interface{} {
	return map[string]interface{}{
		"kills":     p.Kills,
		"deaths":    p.Deaths,
		"offensive": p.Score.Offensive,
		"defensive": p.Score.Defensive,
		"support":   p.Score.Support,
		"combat":    p.Score.Combat,
	}
}

func renderPlayerPosition(p api.GetPlayerResponse) map[string]interface{} {
	return map[string]interface{}{
		"x": p.Position.X,
		"y": p.Position.Y,
		"z": p.Position.Z,
	}
}
