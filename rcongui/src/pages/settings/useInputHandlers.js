const getMaxValue = (key) => {
  switch (key) {
    case 'team_switch_cooldown':
      return 30
    case 'idle_autokick_time':
      return 200
    case 'max_ping_autokick':
      return 2000
    case 'queue_length':
      return 6
    case 'vip_slots_num':
      return 100
    case 'players':
    case 'autobalance_threshold':
      return 50
    default:
      return 100 // Default max value
  }
}

export const useInputHandlers = (pendingSettings, setPendingSettings) => {
  const handleInputChange = (key) => (event) => {
    const type = event.target.type
    const value = type === 'number' ? (event.target.value === '' ? '' : Number(event.target.value)) : event.target.value
    setPendingSettings((prev) => ({ ...prev, [key]: value }))
  }

  const handleBlur = (key) => () => {
    if (pendingSettings[key] < 0) {
      setPendingSettings((prev) => ({ ...prev, [key]: 0 }))
    } else if (pendingSettings[key] > getMaxValue(key)) {
      setPendingSettings((prev) => ({ ...prev, [key]: getMaxValue(key) }))
    }
  }

  const handleToggleChange = (key) => (checked) => {
    setPendingSettings((prev) => ({ ...prev, [key]: checked }))
  }

  const handleSliderChange = (key) => (event, value) => {
    setPendingSettings((prev) => ({ ...prev, [key]: value }))
  }

  const handleSelectChange = (key) => (event) => {
    setPendingSettings((prev) => ({
      ...prev,
      [key]: event.target.value
    }))
  }

  return {
    handleInputChange,
    handleBlur,
    handleToggleChange,
    handleSliderChange,
    handleSelectChange
  }
}
