import { Grid, GridList, GridListTile, makeStyles } from "@material-ui/core";
import React from "react";
import { fromJS } from "immutable";
import "emoji-mart/css/emoji-mart.css";
import { ActionButton } from "./PlayerTile/ActionButton";
import { PlayerHeader } from "./PlayerTile/PlayerHeader";
import { PlayerFlags } from "./PlayerTile/PlayerFlags";
import { PlayerSighthings } from "./PlayerTile/PlayerSighthings";
import { PlayerPenalties } from "./PlayerTile/PlayerPenalties";
import withWidth from "@material-ui/core/withWidth";
import { pure } from "recompose";
import { sizing } from "@material-ui/system";

const result = {
  result: {
    total: 50,
    players: [
      {
        id: 70585,
        steam_id_64: "76561199023068998",
        created: "2020-12-04T21:39:52.239",
        names: [
          {
            id: 75883,
            name: "SmockWeedy",
            steam_id_64: "76561199023068998",
            created: "2020-12-04T21:39:52.256",
            last_seen: "2021-01-16T16:32:44",
          },
        ],
        sessions: [],
        sessions_count: 25,
        total_playtime_seconds: 82291,
        current_playtime_seconds: 8646,
        received_actions: [
          {
            action_type: "PUNISH",
            reason:
              "Svp. Avoir un officier est obligatoire. KICK dans 1min / Having an officer is mandatory, thanks. KICK in 1min.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Yaekin",
            time: "2020-12-07T16:38:48.265",
          },
          {
            action_type: "PUNISH",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Yaekin",
            time: "2020-12-07T16:32:11.354",
          },
        ],
        penalty_count: { PERMABAN: 0, KICK: 0, TEMPBAN: 0, PUNISH: 2 },
        blacklist: null,
        flags: [
          {
            id: 6282,
            flag: "\ud83c\uddeb\ud83c\uddf7",
            comment: "Passed security question",
            modified: "2020-12-04T21:44:49.527",
          },
        ],
        watchlist: null,
        first_seen_timestamp_ms: 1607117977000,
        last_seen_timestamp_ms: 1610814768917,
      },
      {
        id: 3718,
        steam_id_64: "76561197984877751",
        created: "2020-04-30T19:53:33.081",
        names: [
          {
            id: 14585,
            name: "Dr.WeeD",
            steam_id_64: "76561197984877751",
            created: "2020-05-29T19:11:08.389",
            last_seen: "2021-01-16T14:38:47",
          },
          {
            id: 3841,
            name: "Dr.WeeD - FR",
            steam_id_64: "76561197984877751",
            created: "2020-04-30T19:53:33.089",
            last_seen: null,
          },
          {
            id: 15462,
            name: "Dr.WeeD  Fr",
            steam_id_64: "76561197984877751",
            created: "2020-06-01T20:47:35.906",
            last_seen: null,
          },
          {
            id: 13786,
            name: "Dr.WeeD  FR",
            steam_id_64: "76561197984877751",
            created: "2020-05-26T14:44:11.218",
            last_seen: null,
          },
        ],
        sessions: [],
        sessions_count: 738,
        total_playtime_seconds: 3162774,
        current_playtime_seconds: 15483,
        received_actions: [
          {
            action_type: "TEMPBAN",
            reason: "test",
            by: "Dr.WeeD",
            time: "2021-01-02T16:07:45.870",
          },
          {
            action_type: "PERMABAN",
            reason: "test",
            by: "BLACKLIST: Dr.WeeD",
            time: "2021-01-02T15:27:54.919",
          },
          {
            action_type: "TEMPBAN",
            reason: "test",
            by: "Dr.WeeD",
            time: "2021-01-02T02:29:21.258",
          },
          {
            action_type: "PERMABAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Dr.WeeD",
            time: "2020-12-25T12:15:48.332",
          },
          {
            action_type: "TEMPBAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Dr.WeeD",
            time: "2020-12-25T12:14:01.733",
          },
          {
            action_type: "TEMPBAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Dr.WeeD",
            time: "2020-12-25T12:14:01.232",
          },
          {
            action_type: "PERMABAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "BLACKLIST",
            time: "2020-12-25T12:12:17.465",
          },
          {
            action_type: "PERMABAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Dr.WeeD",
            time: "2020-12-25T12:11:43.569",
          },
          {
            action_type: "PERMABAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Dr.WeeD",
            time: "2020-12-24T18:05:51.048",
          },
          {
            action_type: "PERMABAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "BLACKLIST",
            time: "2020-12-24T18:01:31.580",
          },
          {
            action_type: "PERMABAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Dr.WeeD",
            time: "2020-12-24T17:57:55.043",
          },
          {
            action_type: "TEMPBAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Dr.WeeD",
            time: "2020-12-24T17:26:58.147",
          },
          {
            action_type: "TEMPBAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Dr.WeeD",
            time: "2020-12-20T23:22:04.295",
          },
          {
            action_type: "TEMPBAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Dr.WeeD",
            time: "2020-12-20T23:22:02.433",
          },
          {
            action_type: "TEMPBAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Dr.WeeD",
            time: "2020-12-20T23:11:04.254",
          },
          {
            action_type: "TEMPBAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Dr.WeeD",
            time: "2020-12-20T23:04:37.658",
          },
          {
            action_type: "TEMPBAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Dr.WeeD",
            time: "2020-12-20T23:02:42.264",
          },
          {
            action_type: "TEMPBAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Dr.WeeD",
            time: "2020-12-20T23:00:06.767",
          },
          {
            action_type: "TEMPBAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Dr.WeeD",
            time: "2020-12-20T22:58:47.666",
          },
          {
            action_type: "KICK",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Dr.WeeD",
            time: "2020-12-11T20:27:50.084",
          },
          {
            action_type: "PERMABAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: null,
            time: "2020-12-06T13:02:22.158",
          },
          {
            action_type: "PERMABAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "BLACKLIST",
            time: "2020-12-04T00:36:24.868",
          },
          {
            action_type: "PERMABAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "BLACKLIST",
            time: "2020-12-04T00:36:10.969",
          },
          {
            action_type: "PERMABAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: null,
            time: "2020-12-04T00:30:27.271",
          },
          {
            action_type: "PERMABAN",
            reason: "test",
            by: "BLACKLIST",
            time: "2020-12-04T00:27:35.171",
          },
          {
            action_type: "PERMABAN",
            reason: "test",
            by: "BLACKLIST",
            time: "2020-12-04T00:26:48.676",
          },
          {
            action_type: "PERMABAN",
            reason: "test",
            by: "BLACKLIST",
            time: "2020-12-04T00:23:36.817",
          },
          {
            action_type: "PERMABAN",
            reason: "test",
            by: "BLACKLIST",
            time: "2020-12-04T00:22:51.277",
          },
          {
            action_type: "PERMABAN",
            reason: "test",
            by: "",
            time: "2020-12-04T00:12:08.247",
          },
          {
            action_type: "PERMABAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "BLACKLIST",
            time: "2020-12-04T00:06:52.561",
          },
          {
            action_type: "PERMABAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "BLACKLIST",
            time: "2020-12-04T00:06:42.180",
          },
          {
            action_type: "PERMABAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "BLACKLIST",
            time: "2020-12-03T23:54:01.000",
          },
          {
            action_type: "PERMABAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: null,
            time: "2020-12-03T23:53:14.540",
          },
          {
            action_type: "PERMABAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Dr.WeeD",
            time: "2020-12-03T23:52:34.535",
          },
          {
            action_type: "PERMABAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: null,
            time: "2020-12-03T23:33:57.039",
          },
          {
            action_type: "PERMABAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.Toutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "BLACKLIST",
            time: "2020-12-03T12:33:20.916",
          },
          {
            action_type: "TEMPBAN",
            reason: "test",
            by: "Dr.WeeD",
            time: "2020-12-03T12:20:39.412",
          },
          {
            action_type: "PERMABAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.Toutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "BLACKLIST",
            time: "2020-12-03T12:20:13.786",
          },
          {
            action_type: "TEMPBAN",
            reason: "test",
            by: "Dr.WeeD",
            time: "2020-12-03T12:19:35.232",
          },
          {
            action_type: "PERMABAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.Toutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "BLACKLIST",
            time: "2020-12-03T12:18:22.334",
          },
          {
            action_type: "PERMABAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.Toutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Dr.WeeD",
            time: "2020-12-03T11:56:39.683",
          },
          {
            action_type: "TEMPBAN",
            reason: "test",
            by: "Dr.WeeD",
            time: "2020-12-03T11:40:08.011",
          },
          {
            action_type: "PUNISH",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Dr.WeeD",
            time: "2020-12-02T23:21:28.793",
          },
          {
            action_type: "PUNISH",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Dr.WeeD",
            time: "2020-12-02T23:19:31.383",
          },
          {
            action_type: "TEMPBAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Dr.WeeD",
            time: "2020-12-02T21:06:24.349",
          },
          {
            action_type: "TEMPBAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Dr.WeeD",
            time: "2020-12-02T21:02:03.921",
          },
          {
            action_type: "PUNISH",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Dr.WeeD",
            time: "2020-12-02T20:35:32.812",
          },
          {
            action_type: "TEMPBAN",
            reason:
              "Avoir un officier est obligatoire. Having an officer is mandatory.\n\nToutes les regles sur https://discord.io/HLLFR  #regles-serveur (via un navigateur pas directement dans discord)",
            by: "Dr.WeeD",
            time: "2020-12-02T20:31:31.919",
          },
          {
            action_type: "PERMABAN",
            reason: "Miam",
            by: "Dr.WeeD",
            time: "2020-11-18T01:26:05.298",
          },
          {
            action_type: "KICK",
            reason: "dfcgfcvb",
            by: "Dr.WeeD",
            time: "2020-10-12T21:53:02.735",
          },
          {
            action_type: "KICK",
            reason: "test",
            by: "Dr.WeeD",
            time: "2020-09-13T13:08:09.611",
          },
          {
            action_type: "KICK",
            reason:
              "Fellow HLL player, it is peak hour for French players, you're being kicked to make room, sorry for the inconvenience and thank you for your understanding.",
            by: "Dr.WeeD",
            time: "2020-08-06T09:45:29.069",
          },
          {
            action_type: "KICK",
            reason: "Non",
            by: "Youho",
            time: "2020-08-03T20:54:17.665",
          },
          {
            action_type: "PUNISH",
            reason: "test",
            by: "Dr.WeeD",
            time: "2020-07-12T17:10:35.513",
          },
          {
            action_type: "KICK",
            reason:
              "Avoir un officer est obligatoire. 1min avant kick. Having an officer is mandatory. 1min before kick",
            by: "Dr.WeeD",
            time: "2020-07-11T16:15:33.016",
          },
          {
            action_type: "PUNISH",
            reason: "test",
            by: "Dr.WeeD",
            time: "2020-07-01T13:47:00.505",
          },
          {
            action_type: "KICK",
            reason: "Quit",
            by: "Dr.WeeD",
            time: "2020-06-16T20:11:05.092",
          },
          {
            action_type: "SWITCHTEAMNOW",
            reason: "",
            by: "Dr.WeeD",
            time: "2020-05-29T23:18:26.653",
          },
          {
            action_type: "SWITCHTEAMNOW",
            reason: "",
            by: "Dr.WeeD",
            time: "2020-05-29T23:14:59.468",
          },
          {
            action_type: "KICK",
            reason: "Change your nicknaam with alphabet",
            by: "172.18.0.3",
            time: "2020-05-21T14:49:21.273",
          },
          {
            action_type: "SWITCHTEAMNOW",
            reason: "",
            by: "172.18.0.9",
            time: "2020-05-18T09:18:35.773",
          },
          {
            action_type: "PUNISH",
            reason:
              "Merci d\u00e9couter votre chef de squad. Please listend to your leader. YOU NEED A SUPPORT ROLE.",
            by: "172.18.0.9",
            time: "2020-05-15T23:37:17.502",
          },
          {
            action_type: "SWITCHTEAMNOW",
            reason: "",
            by: "172.18.0.9",
            time: "2020-05-15T20:12:48.686",
          },
          {
            action_type: "SWITCHTEAMNOW",
            reason: "",
            by: "172.18.0.4",
            time: "2020-05-13T23:04:05.971",
          },
          {
            action_type: "SWITCHTEAMNOW",
            reason: "",
            by: "172.18.0.4",
            time: "2020-05-13T22:57:47.958",
          },
          {
            action_type: "SWITCHTEAMNOW",
            reason: "",
            by: "172.18.0.4",
            time: "2020-05-12T20:39:39.064",
          },
          {
            action_type: "SWITCHTEAMNOW",
            reason: "",
            by: "172.18.0.4",
            time: "2020-05-12T20:38:56.273",
          },
          {
            action_type: "SWITCHTEAMNOW",
            reason: "",
            by: "172.18.0.4",
            time: "2020-05-12T19:18:38.271",
          },
          {
            action_type: "SWITCHTEAMNOW",
            reason: "",
            by: "172.18.0.4",
            time: "2020-05-10T21:34:14.395",
          },
          {
            action_type: "SWITCHTEAMNOW",
            reason: "",
            by: "172.18.0.4",
            time: "2020-05-07T09:49:22.436",
          },
        ],
        penalty_count: { PERMABAN: 27, KICK: 8, TEMPBAN: 18, PUNISH: 6 },
        blacklist: {
          steam_id_64: "76561197984877751",
          is_blacklisted: false,
          reason: "test",
          by: "Dr.WeeD",
        },
        flags: [
          {
            id: 711,
            flag: "\ud83d\udea8",
            comment: "",
            modified: "2020-07-10T16:02:57.428",
          },
          {
            id: 2751,
            flag: "\ud83e\udd13",
            comment: "Nerd",
            modified: "2020-08-16T23:59:11.095",
          },
          {
            id: 5321,
            flag: "\ud83c\uddeb\ud83c\uddf7",
            comment: "Passed security question",
            modified: "2020-11-03T17:13:44.856",
          },
        ],
        watchlist: {
          id: 1,
          steam_id_64: "76561197984877751",
          is_watched: false,
          reason: "Dr.WeeD is in the place",
          comment: "",
        },
        first_seen_timestamp_ms: 1588276406851,
        last_seen_timestamp_ms: 1610808440000,
      },
      {
        id: 9197,
        steam_id_64: "76561198380054723",
        created: "2020-05-13T12:21:38.678",
        names: [
          {
            id: 9566,
            name: "WEED_M8",
            steam_id_64: "76561198380054723",
            created: "2020-05-13T12:21:38.700",
            last_seen: "2021-01-09T19:04:19",
          },
        ],
        sessions: [],
        sessions_count: 2,
        total_playtime_seconds: 3218,
        current_playtime_seconds: 604352,
        received_actions: [],
        penalty_count: { PERMABAN: 0, KICK: 0, TEMPBAN: 0, PUNISH: 0 },
        blacklist: null,
        flags: [],
        watchlist: null,
        first_seen_timestamp_ms: 1589372497355,
        last_seen_timestamp_ms: 1610219128000,
      },
      {
        id: 60762,
        steam_id_64: "76561198264806309",
        created: "2020-11-05T19:39:45.906",
        names: [
          {
            id: 64968,
            name: "Asteroweed",
            steam_id_64: "76561198264806309",
            created: "2020-11-05T19:39:45.953",
            last_seen: "2021-01-09T11:33:20",
          },
        ],
        sessions: [],
        sessions_count: 11,
        total_playtime_seconds: 20639,
        current_playtime_seconds: 631411,
        received_actions: [
          {
            action_type: "PUNISH",
            reason:
              "Svp. Avoir un officier est obligatoire. KICK dans 1min / Having an officer is mandatory, thanks. KICK in 1min.",
            by: "Boubou",
            time: "2020-11-12T20:51:18.932",
          },
        ],
        penalty_count: { PERMABAN: 0, KICK: 0, TEMPBAN: 0, PUNISH: 1 },
        blacklist: null,
        flags: [],
        watchlist: null,
        first_seen_timestamp_ms: 1604605174036,
        last_seen_timestamp_ms: 1610193537000,
      },
      {
        id: 83188,
        steam_id_64: "76561198130202221",
        created: "2021-01-01T02:47:25.353",
        names: [
          {
            id: 89617,
            name: "MarsWeed",
            steam_id_64: "76561198130202221",
            created: "2021-01-01T02:47:25.362",
            last_seen: "2021-01-01T19:56:00",
          },
        ],
        sessions: [],
        sessions_count: 3,
        total_playtime_seconds: 1898,
        current_playtime_seconds: 1292451,
        received_actions: [],
        penalty_count: { PERMABAN: 0, KICK: 0, TEMPBAN: 0, PUNISH: 0 },
        blacklist: null,
        flags: [],
        watchlist: null,
        first_seen_timestamp_ms: 1609469242000,
        last_seen_timestamp_ms: 1609531195000,
      },
      {
        id: 77948,
        steam_id_64: "76561198199597381",
        created: "2020-12-19T21:26:41.646",
        names: [
          {
            id: 83936,
            name: "weedtommy",
            steam_id_64: "76561198199597381",
            created: "2020-12-19T21:26:41.660",
            last_seen: null,
          },
        ],
        sessions: [],
        sessions_count: 2,
        total_playtime_seconds: 9955,
        current_playtime_seconds: 1679115,
        received_actions: [],
        penalty_count: { PERMABAN: 0, KICK: 0, TEMPBAN: 0, PUNISH: 0 },
        blacklist: null,
        flags: [],
        watchlist: null,
        first_seen_timestamp_ms: 1608413207000,
        last_seen_timestamp_ms: 1609150596000,
      },
      {
        id: 6856,
        steam_id_64: "76561198937597812",
        created: "2020-05-08T11:00:43.525",
        names: [
          {
            id: 69412,
            name: "i smoke weed everyda",
            steam_id_64: "76561198937597812",
            created: "2020-11-19T12:42:54.773",
            last_seen: null,
          },
        ],
        sessions: [],
        sessions_count: 10,
        total_playtime_seconds: 2791,
        current_playtime_seconds: 1755196,
        received_actions: [],
        penalty_count: { PERMABAN: 0, KICK: 0, TEMPBAN: 0, PUNISH: 0 },
        blacklist: null,
        flags: [],
        watchlist: null,
        first_seen_timestamp_ms: 1588935643266,
        last_seen_timestamp_ms: 1609068299000,
      },
    ],
    page: 1,
    page_size: 10,
  },
  command: "players_history",
  arguments: { page_size: 10, page: 1, player_name: "weed" },
  failed: false,
};

const useStyles = makeStyles((theme) => ({
  paperTile: {
    backgroundColor: theme.palette.background.paper,
    minHeight: "100%",
    padding: theme.spacing(2),
  },
  root: {
    display: "flex",
    flexWrap: "wrap",
    justifyContent: "space-around",
    overflow: "hidden",
  },
}));

const PlayerGrid = withWidth()(
  ({
    classes,
    players,
    onBlacklist,
    onUnBlacklist,
    onUnban,
    onflag,
    onDeleteFlag,
    onAddVip,
    onDeleteVip,
    onTempBan,
    onAddToWatchList,
    onRemoveFromWatchList,
    width,
    vips,
  }) => {
    //const players = fromJS(result.result.players);
    const myClasses = useStyles();

    const size = {
      xs: 1,
      sm: 2,
      md: 3,
      lg: 4,
      xl: 5,
    }[width];

    return (
      <Grid container>
        <Grid item xs={12}>
          <GridList cols={size} cellHeight={210} spacing={12}>
            {players.map((player) => {
              return (
                <GridListTile
                  key={player.get("steam_id_64")}
                  style={{ minHeight: "100%" }}
                >
                  <Grid
                    container
                    className={myClasses.paperTile}
                    direction="column"
                    justify="space-between"
                  >
                    <PlayerHeader classes={classes} player={player} />
                      <React.Fragment>
                        <PlayerFlags
                          player={player}
                          classes={classes}
                          onDeleteFlag={onDeleteFlag}
                        />
                        <PlayerSighthings classes={classes} player={player} />
                        <PlayerPenalties classes={classes} player={player} />
                        <Grid container justify="center">
                          <Grid item>
                            <ActionButton
                              blacklisted={
                                player.get("blacklist") &&
                                player.get("blacklist").get("is_blacklisted")
                              }
                              onUnBlacklist={() => onUnBlacklist(player)}
                              onBlacklist={() => onBlacklist(player)}
                              onTempBan={() => onTempBan(player)}
                              onUnban={() => onUnban(player)}
                              onflag={() => onflag(player)}
                              isVip={vips.get(player.get("steam_id_64"))}
                              onAddVip={() => onAddVip(player)}
                              onDeleteVip={() => onDeleteVip(player)}
                              isWatched={
                                player.get("watchlist") &&
                                player.get("watchlist").get("is_watched")
                              }
                              onAddToWatchList={() => onAddToWatchList(player)}
                              onRemoveFromWatchList={() =>
                                onRemoveFromWatchList(player)
                              }
                            />
                          </Grid>
                        </Grid>
                      </React.Fragment>
                  </Grid>
                </GridListTile>
              );
            })}
          </GridList>
        </Grid>
      </Grid>
    );
  }
);

export default pure(PlayerGrid);
