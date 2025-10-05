package crcon

type AutoModSeedingConfig struct {
	Enabled         bool
	DryRun          bool
	EnforceCapFight EnforceCapFight
}

func (c *AutoModSeedingConfig) Equals(o *AutoModSeedingConfig) bool {
	if o == nil {
		return false
	}
	if c.Enabled != o.Enabled || c.DryRun != o.DryRun || !c.EnforceCapFight.Equals(o.EnforceCapFight) {
		return false
	}
	return true
}

type EnforceCapFight struct {
	MinPlayers       int
	MaxPlayers       int
	MaxCaps          int
	SkipWarning      bool
	ViolationMessage string
}

func (c *EnforceCapFight) Equals(o EnforceCapFight) bool {
	return c.MinPlayers == o.MinPlayers ||
		c.MaxPlayers == o.MaxPlayers ||
		c.MaxCaps == o.MaxCaps ||
		c.SkipWarning == o.SkipWarning ||
		c.ViolationMessage == o.ViolationMessage
}
