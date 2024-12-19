export const padlockConfigs = [
  { name: 'allow_opt_out', label: 'Allow user to opt-out of vote map reminders by typing !votemap never' },
  { name: 'consider_offensive_same_map', label: 'Consider offensive maps as being the same when excluding:' },
  { name: 'consider_skirmishes_as_same_map', label: 'Consider skirmish maps as being the same when excluding:' },
  { name: 'allow_consecutive_offensives', label: 'Allow consecutive offensive map' },
  {
    name: 'allow_consecutive_offensives_opposite_sides',
    label: 'Allow consecutive offensive where a team would play defense twice in a row. E.g off_ger followed by off_us'
  },
  { name: 'allow_consecutive_skirmishes', label: 'Allow consecutive skirmish map' },
  { name: 'allow_default_to_offensive', label: 'Allow default map to be an offensive' },
  { name: 'allow_default_to_skirmish', label: 'Allow default map to be a skirmish' }
]

export const messageFieldConfigs = [
  {
    name: 'instruction_text',
    label: 'Reminder text sent to player to vote:',
    helperText: 'Make sure you add {map_selection} in your text',
    rows: 10
  },
  {
    name: 'thank_you_text',
    label: 'Thank you for voting message:',
    helperText:
      "The reply to player after they voted. You can use {player_name} and {map_name} in the text. Leave blank if you don't want the confirmation message",
    rows: 10
  },
  {
    name: 'help_text',
    label: 'Help text:',
    helperText:
      'This text will show to the player in case of a bad !votemap command, or if the user types !votemap help',
    rows: 10
  }
]

export const textFieldConfigs = [
  {
    name: 'reminder_frequency_minutes',
    label: 'Reminder frequency minutes:',
    helperText:
      "Will remind players who haven't voted with a PM. Set to 0 to disable (will only show once on map end).",
    inputProps: { min: 0, max: 90 }
  },
  {
    name: 'num_warfare_options',
    label: 'Warfare',
    helperText: 'Number of warfare maps to offer'
  },
  {
    name: 'num_offensive_options',
    label: 'Offensive',
    helperText: 'Number of offensive maps to offer'
  },
  {
    name: 'num_skirmish_control_options',
    label: 'Control Skirmish',
    helperText: 'Number of control skirmish maps to offer'
  },
  {
    name: 'number_last_played_to_exclude',
    label: 'Number of recently played maps excluded:',
    helperText: 'Exclude the last N played maps from the selection. The current map is always excluded.',
    inputProps: { min: 0, max: 6, step: 1 }
  }
]

export const defaultMapOptions = [
  {
    name: 'least_played_from_suggestions',
    label: 'Pick least played map from suggestions'
  },
  {
    name: 'least_played_from_all_map',
    label: 'Pick least played map from all maps'
  },
  {
    name: 'random_from_suggestions',
    label: ' Pick randomly from suggestions'
  },
  {
    name: 'random_from_all_maps',
    label: 'Pick randomly from all maps'
  }
]
