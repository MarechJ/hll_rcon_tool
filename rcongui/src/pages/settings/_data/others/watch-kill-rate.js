const watchKillStreamNotes = `
  {
    "enabled": true,
    "match_start_cooldown_secs": 180,
    "watch_interval_secs": 60,
    "report_cooldown_mins": 5,
    "min_kills": 10,
    "killrate_threshold": 0.5,
    "killrate_threshold_armor": 0.5,
    "killrate_threshold_artillery": 0.5,
    "killrate_threshold_mg": 0.5,
    "only_report_once_per_match": true,
    "whitelist_flags": [],
    "whitelist_armor": false,
    "whitelist_artillery": false,
    "whitelist_mg": false,
    "author": "CRCON Watch KillRate",
    "webhooks": [
      {
        "url": "https://discord.com/api/webhooks/.../...",
        "user_mentions": [],
        "role_mentions": []
      }
    ]
  }
  `;

export default watchKillStreamNotes;
