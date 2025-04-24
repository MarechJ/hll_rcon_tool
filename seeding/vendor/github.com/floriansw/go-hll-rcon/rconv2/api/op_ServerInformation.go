package api

import (
	"fmt"
	"math"
	"slices"
)

type ServerInformationName string

type SupportedPlatform string

const (
	ServerInformationNamePlayers      = "players"
	ServerInformationNamePlayer       = "player"
	ServerInformationNameMapRotation  = "maprotation"
	ServerInformationNameMapSequence  = "mapsequence"
	ServerInformationNameSession      = "session"
	ServerInformationNameServerConfig = "serverconfig"

	PlayerPlatformSteam = PlayerPlatform("steam")

	SupportedPlatformSteam   = "Steam"
	SupportedPlatformWindows = "WinGDK"
	SupportedPlatformEos     = "eos"
)

const (
	PlayerTeamGer = iota
	PlayerTeamUs
	PlayerTeamRus
	PlayerTeamGb
	PlayerTeamDak
	PlayerTeamB8a
)

const (
	PlayerRoleRifleman = iota
	PlayerRoleAssault
	PlayerRoleAutomaticRifleman
	PlayerRoleMedic
	PlayerRoleSpotter
	PlayerRoleSupport
	PlayerRoleHeavyMachineGunner
	PlayerRoleAntiTank
	PlayerRoleEngineer
	PlayerRoleOfficer
	PlayerRoleSniper
	PlayerRoleCrewman
	PlayerRoleTankCommander
	PlayerRoleArmyCommander
)

var (
	requiresValue = []ServerInformationName{
		ServerInformationNamePlayer,
	}
)

type ServerInformation struct {
	Name  ServerInformationName `json:"Name"`
	Value string                `json:"Value"`
}

func (s ServerInformation) Validate() error {
	if slices.Contains(requiresValue, s.Name) && s.Value == "" {
		return fmt.Errorf("%s command requires a Value", s.Name)
	}
	return nil
}

type GetPlayersResponse struct {
	Players []GetPlayerResponse `json:"players"`
}

type PlayerPlatform string

type PlayerTeam int
type PlayerRole int

type GetPlayerResponse struct {
	Id                   string         `json:"iD"`
	Platform             PlayerPlatform `json:"platform"`
	Name                 string         `json:"name"`
	ClanTag              string         `json:"clanTag"`
	EpicOnlineServicesId string         `json:"eOSID"`
	Level                int            `json:"level"`
	Team                 PlayerTeam     `json:"team"`
	Role                 PlayerRole     `json:"role"`
	Squad                string         `json:"platoon"`
	Loadout              string         `json:"loadout"`
	Kills                int            `json:"kills"`
	Deaths               int            `json:"deaths"`
	Score                ScoreData      `json:"scoreData"`
	Position             WorldPosition  `json:"worldPosition"`
}

type ScoreData struct {
	Combat    int `json:"cOMBAT"`
	Offensive int `json:"offense"`
	Defensive int `json:"defense"`
	Support   int `json:"support"`
}

type WorldPosition struct {
	X float64 `json:"x"`
	Y float64 `json:"y"`
	Z float64 `json:"z"`
}

func (w WorldPosition) Equal(o WorldPosition) bool {
	return w.X == o.X && w.Y == o.Y && w.Z == o.Y
}

// IsSpawned indicates that the player is currently not on the map, e.g. in the spawn or team selection screen.
func (w WorldPosition) IsSpawned() bool {
	return (w.X + w.Y + w.Z) != 0
}

// Distance calculates the distance of this and another position in the game world. This includes movement on the x-axis
// (as represented in changed values of X and Y) as well as on the y-axis (represented by changed Z values).
// This is calculated as if the distance was travelled in a straight line without observing obstacles. It depends on the
// resolution of when the two involved positions were obtained how accurate the calculated distance is.
func (w WorldPosition) Distance(o WorldPosition) Distance {
	return Distance(math.Sqrt(math.Pow(w.X-o.X, 2) + math.Pow(w.Y-o.Y, 2) + math.Pow(w.Z-o.Z, 2)))
}

type DrawableMap interface {
	mapData() *mapData
}

var (
	xs     = []string{"A", "B", "C", "D", "E", "F", "G", "H", "I", "J"}
	numpad = [][]int{
		{7, 8, 9},
		{4, 5, 6},
		{1, 2, 3},
	}
)

func (w WorldPosition) Grid(m DrawableMap) Grid {
	d := m.mapData()
	if d == nil {
		return Grid{}
	}
	x := w.X - d.MapCenterOffset.X
	y := w.Y - d.MapCenterOffset.Y
	xGrid, yGrid := math.Floor(x/d.SectorSize), math.Floor(y/d.SectorSize)

	xInGrid := x - xGrid*d.SectorSize
	yInGrid := y - yGrid*d.SectorSize
	num := d.SectorSize / 3
	return Grid{
		X:      xs[int(xGrid)+5],
		Y:      int(yGrid) + 6,
		Numpad: numpad[int(math.Abs(math.Floor(yInGrid/num)))][int(math.Abs(math.Floor(xInGrid/num)))],
	}
}

// Distance is supposed to be in centimeters (default unit of worlds in Unreal Engine)
type Distance float64

func (d Distance) Meters() float64 {
	return float64(d) / 100
}

func (d Distance) Add(o Distance) Distance {
	return d + o
}

type GetServerConfigResponse struct {
	ServerName         string              `json:"serverName"`
	Build              string              `json:"buildNumber"`
	BuildRevision      string              `json:"buildRevision"`
	SupportedPlatforms []SupportedPlatform `json:"supportedPlatforms"`
}

type GetSessionResponse struct {
	ServerName       string `json:"serverName"`
	MapName          string `json:"mapName"`
	GameMode         string `json:"gameMode"`
	MaxPlayerCount   int    `json:"maxPlayerCount"`
	PlayerCount      int    `json:"playerCount"`
	MaxQueueCount    int    `json:"maxQueueCount"`
	QueueCount       int    `json:"queueCount"`
	MaxVIPQueueCount int    `json:"maxVIPQueueCount"`
	VIPQueueCount    int    `json:"vIPQueueCount"`
}

type Vector2D struct {
	X float64
	Y float64
}

type mapData struct {
	SectorSize float64
	// by default the center of the map is at vector 0,0, however, some maps (like Carentan Skirmish)
	// move the center of the map (as visual to the player) on the x and/or y-axis. MapCenterOffset is the Vector
	// that describes this offset. It has 0,0 by default.
	MapCenterOffset Vector2D
}

// maps describe the default configuration of a map, or a specific different config if a map
// is different to the default.
var maps = map[string]map[string]mapData{
	"Skirmish": {
		"default": {
			SectorSize: 13926,
		},
		"CARENTAN": {
			SectorSize:      13926,
			MapCenterOffset: Vector2D{X: 150, Y: -110},
		},
		"MORTAIN": {
			SectorSize:      13926,
			MapCenterOffset: Vector2D{X: 100, Y: 0},
		},
		"ST MARIE DU MONT": {
			SectorSize:      13926,
			MapCenterOffset: Vector2D{X: 0, Y: -27852.799},
		},
		"DRIEL": {
			SectorSize:      13926,
			MapCenterOffset: Vector2D{X: -20, Y: 28190},
		},
	},
	"Warfare": {
		// all older maps (SME, SMDM, etc) have a default sector width and height
		"default": {
			SectorSize: 19840,
		},
		// Carentan has a slightly higher sector size
		"CARENTAN": {
			SectorSize: 20160,
		},
		// newer maps have a 200x200m grid schema
		"ELSENBORN RIDGE": {
			SectorSize: 20000,
		},
		"MORTAIN": {
			SectorSize: 20000,
		},
		"TOBRUK": {
			SectorSize: 20000,
		},
	},
}

func (m GetSessionResponse) mapData() *mapData {
	if mode, exists := maps[m.GameMode]; !exists {
		return nil
	} else if md, exists := mode[m.MapName]; exists {
		return &md
	} else if d, exists := mode["default"]; exists {
		return &d
	} else {
		return nil
	}
}

// GridSize returns the size in meters of a grid square on the map, depending on the current game mode.
func (m GetSessionResponse) GridSize() float64 {
	if d := m.mapData(); d != nil {
		return d.SectorSize
	}
	return 0
}

type GetMapRotationResponse struct {
	Maps []Map `json:"mAPS"`
}

type GetMapSequenceResponse struct {
	Maps []Map `json:"mAPS"`
}

type Map struct {
	Name      string `json:"name"`
	GameMode  string `json:"gameMode"`
	TimeOfDay string `json:"timeOfDay"`
	Id        string `json:"iD"`
	Position  int    `json:"position"`
}

type Grid struct {
	X      string
	Y      int
	Numpad int
}

func (g Grid) String() string {
	return fmt.Sprintf("%s%d Numpad %d", g.X, g.Y, g.Numpad)
}
