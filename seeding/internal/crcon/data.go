package crcon

type AutoModSeedingConfig struct {
	Enabled         bool
	DryRun          bool
	EnforceCapFight EnforceCapFight
}

type EnforceCapFight struct {
	MinPlayers       int
	MaxPlayers       int
	MaxCaps          int
	SkipWarning      bool
	ViolationMessage string
}
