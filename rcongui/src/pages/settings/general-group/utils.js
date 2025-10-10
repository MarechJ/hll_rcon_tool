export const getMaxValue = (key) => {
  switch (key) {
    case "team_switch_cooldown":
      return 30;
    case "idle_autokick_time":
      return 200;
    case "max_ping_autokick":
      return 2000;
    case "queue_length":
      return 6;
    case "vip_slots_num":
      return 100;
    case "match_warfare_timer":
      return 180;
    case "match_offensive_timer":
      return 300;
    case "match_skirmish_timer":
      return 60;
    case "warmup_skirmish_timer":
    case "warmup_warfare_timer":
      return 10;
    case "players":
    case "autobalance_threshold":
      return 50;
    default:
      return 100;
  }
};

export const getMinValue = (key) => {
  switch (key) {
    case "match_warfare_timer":
      return 30;
    case "match_offensive_timer":
      return 50;
    case "match_skirmish_timer":
      return 10;
    case "warmup_warfare_timer":
    case "warmup_skirmish_timer":
      return 1;
    default:
      return 0;
  }
};

export const getMarks = (key) => {
  switch (key) {
    case "team_switch_cooldown":
      return [0, 5, 10, 15, 20, 25, 30].map((val) => ({
        value: val,
        label: `${val}`,
      }));
    case "idle_autokick_time":
      return [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200].map((val) => ({
        value: val,
        label: `${val}`,
      }));
    case "max_ping_autokick":
      return [0, 500, 1000, 1500, 2000].map((val) => ({
        value: val,
        label: `${val}`,
      }));
    case "queue_length":
      return [0, 1, 2, 3, 4, 5, 6].map((val) => ({
        value: val,
        label: `${val}`,
      }));
    case "vip_slots_num":
      return [0, 20, 40, 60, 80, 100].map((val) => ({
        value: val,
        label: `${val}`,
      }));
    default:
      return [];
  }
};

export const getHelpText = (key) => {
  switch (key) {
    case "autobalance_threshold":
      return "0 means the teams must match exactly";
    case "autobalance_enabled":
      return "Autobalance will automatically move players around to balance the teams.";
    case "queue_length":
      return "Recommended value: 6";
    case "vip_slots_num":
      return "Recommended value: 1-2";
    case "match_warfare_timer":
      return "Default is 90 minutes";
    case "match_offensive_timer":
      return "Default is 150 minutes";
    case "match_skirmish_timer":
      return "Default is 30 minutes";
    case "warmup_warfare_timer":
    case "warmup_skirmish_timer":
      return "Default is 3 minutes";
    case "votekick_thresholds":
      return "Set the number of votes required to kick a player based on the number of players in the team. The first field defines the minimum number of players in the team, and the second field defines the number of votes required. Reasonable values are [0, 1], [10, 5], [25, 12], [50, 20].";
    default:
      return "0 to disable";
  }
};

export const getStep = (key) => {
  switch (key) {
    case "team_switch_cooldown":
      return 1;
    case "idle_autokick_time":
    case "max_ping_autokick":
      return 10;
    case "queue_length":
    case "vip_slots_num":
      return 1;
    case "warfare_match_timer":
    case "offensive_match_timer":
    case "skirmish_match_timer":
      return 5;
    default:
      return 1;
  }
};

export const getTooltipText = (key) =>
  ({
    team_switch_cooldown:
      "The time a player must wait before switching to another team. Set 0 to disable.",
    idle_autokick_time:
      "Minutes of inactivity before a player is automatically kicked. Set 0 to disable.",
    max_ping_autokick:
      "Maximum allowed ping (ms) before a player is automatically kicked. Set 0 to disable.",
    queue_length:
      "Maximum number of players allowed to wait in the server queue.",
    autobalance_enabled:
      "When enabled, the server will enforce autobalance thresholds.",
    autobalance_threshold:
      "Maximum team size difference allowed before autobalance intervenes. 0 requires equal teams.",
    vip_slots_num:
      "Number of reserved VIP slots. VIPs can join even when the server is full.",
    votekick_enabled: "Enable or disable the in-game votekick system.",
    votekick_thresholds:
      "Threshold pairs defining required votes by team size: [min players, required votes].",
    autovotekick_conditions:
      "Ingame moderators are those who are actually playing the game on the server. Online moderators are those who are logged in CRCON's interface.",
    enabled:
      "When enabled, this feature manages the in-game votekicks by turning them off if the specified conditions are met, and turning them back on if they are not met.",
  }[key]);
