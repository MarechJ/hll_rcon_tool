package data

import (
	"github.com/floriansw/go-hll-rcon/rconv2/api"
	"gopkg.in/yaml.v3"
	"log/slog"
	"os"
	"slices"
)

type Fence struct {
	X         *string    `yaml:"X,omitempty"`
	Y         *int       `yaml:"Y,omitempty"`
	Numpads   []int      `yaml:"Numpad,omitempty"`
	Condition *Condition `yaml:"Condition,omitempty"`
}

func (f Fence) Includes(w api.Grid) bool {
	if f.X != nil && w.X != *f.X {
		return false
	}
	if f.Y != nil && w.Y != *f.Y {
		return false
	}
	if len(f.Numpads) == 0 {
		return true
	}
	return slices.Contains(f.Numpads, w.Numpad)
}

func (f Fence) Matches(si *api.GetSessionResponse) bool {
	if f.Condition == nil {
		return true
	}
	return f.Condition.Matches(si)
}

type Condition struct {
	Equals      map[string][]string `yaml:"Equals,omitempty"`
	LessThan    map[string]int      `yaml:"LessThan,omitempty"`
	GreaterThan map[string]int      `yaml:"GreaterThan,omitempty"`
}

func (c Condition) Matches(si *api.GetSessionResponse) bool {
	if len(c.Equals) == 0 && len(c.LessThan) == 0 && len(c.GreaterThan) == 0 {
		return true
	}
	for k, v := range c.Equals {
		if k == "map_name" && slices.Contains(v, si.MapName) {
			continue
		}
		if k == "game_mode" && slices.Contains(v, si.GameMode) {
			continue
		}
		return false
	}
	for k, v := range c.LessThan {
		if k == "player_count" && si.PlayerCount < v {
			continue
		}
		return false
	}
	for k, v := range c.GreaterThan {
		if k == "player_count" && si.PlayerCount > v {
			continue
		}
		return false
	}
	return true
}

type Server struct {
	Host               string    `yaml:"Host"`
	Port               int       `yaml:"Port"`
	Password           string    `yaml:"Password"`
	PunishAfterSeconds *int      `yaml:"PunishAfterSeconds,omitempty"`
	AxisFence          []Fence   `yaml:"AxisFence"`
	AlliesFence        []Fence   `yaml:"AlliesFence"`
	Messages           *Messages `yaml:"Messages,omitempty"`
}

func (s Server) WarningMessage() string {
	if s.Messages == nil || s.Messages.Warning == nil {
		return "You are outside of the designated play area! Please go back to the battlefield immediately.\n\nYou will be punished in %s"
	}
	return *s.Messages.Warning
}

func (s Server) PunishMessage() string {
	if s.Messages == nil || s.Messages.Punish == nil {
		return "%s outside the play area"
	}
	return *s.Messages.Punish
}

type Messages struct {
	Warning *string `yaml:"Warning,omitempty"`
	Punish  *string `yaml:"Punish,omitempty"`
}

type Config struct {
	Servers []Server `yaml:"Servers"`
	path    string
}

func (c *Config) Save() error {
	config, err := yaml.Marshal(c)
	if err != nil {
		return err
	}
	return os.WriteFile(c.path, config, 0655)
}

func NewConfig(path string, logger *slog.Logger) (*Config, error) {
	config, err := readConfig(path, logger)
	if err != nil {
		return config, err
	}

	return config, config.Save()
}

func readConfig(path string, logger *slog.Logger) (*Config, error) {
	var config Config
	if _, err := os.Stat(path); os.IsNotExist(err) {
		logger.Info("create-config")
		config = Config{}
	} else {
		logger.Info("read-existing-config")
		c, err := os.ReadFile(path)
		if err != nil {
			return &Config{}, err
		}
		err = yaml.Unmarshal(c, &config)
		if err != nil {
			return &Config{}, err
		}
	}
	config.path = path
	return &config, nil
}
