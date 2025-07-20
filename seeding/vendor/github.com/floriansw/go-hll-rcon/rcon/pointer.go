package rcon

func toInt(v *int) int {
	if v == nil {
		return 0
	}
	return *v
}

func fromInt(v int) *int {
	return &v
}
