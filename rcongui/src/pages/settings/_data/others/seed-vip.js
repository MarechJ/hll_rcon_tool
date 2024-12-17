const SeedVipNotes = `
{
    "enabled": true,
    "dry_run": false,

    /* Any one of these language codes should work: 'ar_JO', 'ar_DZ', 'de_DE', 'ru_RU', 'sv_SE', 'uk_UA', 'ar_EG', 'ar_MA', 'ja_JP', 'sk_SK', 'ar_BH', 'fr_FR', 'iw_IL', 'sl_SI', 'bn_BD', 'eu_ES', 'ar_AE', 'id_ID', 'ar_KW', 'ca_ES', 'ar_LY', 'it_IT', 'ar_SD', 'ar_SY', 'es_ES', 'ar_SA', 'pt_PT', 'zh_HK', 'da_DK', 'tlh_QS', 'ar_IQ', 'ko_KR', 'pl_PL', 'vi_VN', 'nl_NL', 'ar_OM', 'fa_IR', 'ar_TN', 'ar_LB', 'tr_TR', 'fi_FI', 'ar_QA', 'hu_HU', 'ar_YE', 'in_ID', 'nb_NO', 'zh_CN', 'el_GR', 'he_IL', 'pt_BR' */
    "language": null,

    /* A list of webhooks for reporting seeding status*/
    "hooks": [
      {"url": "https://...."}
    ],
    /* Which player counts to post an announcement for if any webhooks are set */
    "player_announce_thresholds": [
      10,
      20,
      30
    ],
    /* How frequently to check when the server is below the seeding cut off */
    "poll_time_seeding": 30,
    /* How frequently to check when the server is above the seeding cut off */
    "poll_time_seeded": 300,
    
    /* Uses humane style dates/times when enabled (in X days, hours, etc style messages) */
    "nice_time_delta": true,
    "nice_expiration_date": true,
    
    "requirements": {
      /* How long after the server has seeded to check, this prevents message/VIP spamming if you hover near your seed limit */
      "buffer": {
        "seconds": 0,
        "minutes": 10,
        "hours": 0
      },
      /* The minimum players before you consider seeding by team */
      "min_allies": 0,
      "min_axis": 0,
      /* The number of players for the server to be 'seeded' */
      "max_allies": 25,
      "max_axis": 25,
      /* Whether a player needs to still be connected when the server seeds to get VIP */
      "online_when_seeded": true,
      /* The minimum amount of time a player has to be connected during seeding to be rewarded, it is the sum of all of the fields */
      "minimum_play_time": {
        "seconds": 0,
        "minutes": 5,
        "hours": 0
      }
    },
    "player_messages": {
      /* The format of the discord webhook messages */
      "seeding_in_progress_message": "Server has reached {player_count} players",
      "seeding_complete_message": "Server is live!",
      "player_count_message": "{num_allied_players} - {num_axis_players}",
      
      /* The message sent to a connected player when they are granted VIP */
      "reward_player_message": "Thank you for helping us seed.

You've been granted {vip_reward} of VIP

Your VIP currently expires: {vip_expiration}",
      /* The message sent to a connected player when they did not earn VIP */
      "reward_player_message_no_vip": "Thank you for helping us seed.

The server is now live and the regular rules apply."
    },
    "reward": {
      /* Whether to send the VIP command to the other connected game servers hosted in the same CRCON */
      "forward": false,
      /* The description when adding VIP to a player who does not have VIP */
      "player_name_format_not_current_vip": "{player_name} - CRCON Seed VIP",
      /* When true, it will add their VIP reward if they have VIP, false will overwrite */
      "cumulative": true,
      /* The VIP time to give to the player, it is the sum of all of the fields */
      "timeframe": {
        "minutes": 0,
        "hours": 0,
        "days": 1,
        "weeks": 0
      }
    }
  }
  

`

export default SeedVipNotes
