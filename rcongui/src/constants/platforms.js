import {
    faEdgeLegacy,
  faFortAwesome,
  faPlaystation,
  faSteam,
  faXbox,
} from "@fortawesome/free-brands-svg-icons";
import { faGamepad } from "@fortawesome/free-solid-svg-icons";

export const PLATFORMS = {
  STEAM: "steam",
  EPIC: "epic",
  XBOX_LIVE: "xbl",
  XBOX_SERIES_X: "xsx",
  PLAYSTATION_NETWORK: "psn",
  PLAYSTATION_5: "ps5",
};

export const PLATFORMS_TO_ICON = {
  [PLATFORMS.STEAM]: faSteam,
  [PLATFORMS.EPIC]: faEdgeLegacy,
  [PLATFORMS.XBOX_LIVE]: faXbox,
  [PLATFORMS.XBOX_SERIES_X]: faXbox,
  [PLATFORMS.PLAYSTATION_NETWORK]: faPlaystation,
  [PLATFORMS.PLAYSTATION_5]: faPlaystation,
};

export const PLATFORMS_TO_LABELS = {
  [PLATFORMS.STEAM]: "Steam",
  [PLATFORMS.EPIC]: "Epic",
  [PLATFORMS.XBOX_LIVE]: "Xbox Live",
  [PLATFORMS.XBOX_SERIES_X]: "Xbox X",
  [PLATFORMS.PLAYSTATION_NETWORK]: "PSN",
  [PLATFORMS.PLAYSTATION_5]: "PS5",
};

export const getAllPlatforms = () => [
  {
    value: PLATFORMS.STEAM,
    label: PLATFORMS_TO_LABELS[PLATFORMS.STEAM],
    icon: PLATFORMS_TO_ICON[PLATFORMS.STEAM],
  },
  {
    value: PLATFORMS.EPIC,
    label: PLATFORMS_TO_LABELS[PLATFORMS.EPIC],
    icon: PLATFORMS_TO_ICON[PLATFORMS.EPIC],
  },
  {
    value: PLATFORMS.XBOX_LIVE,
    label: PLATFORMS_TO_LABELS[PLATFORMS.XBOX_LIVE],
    icon: PLATFORMS_TO_ICON[PLATFORMS.XBOX_LIVE],
  },
  {
    value: PLATFORMS.XBOX_SERIES_X,
    label: PLATFORMS_TO_LABELS[PLATFORMS.XBOX_SERIES_X],
    icon: PLATFORMS_TO_ICON[PLATFORMS.XBOX_SERIES_X],
  },
  {
    value: PLATFORMS.PLAYSTATION_NETWORK,
    label: PLATFORMS_TO_LABELS[PLATFORMS.PLAYSTATION_NETWORK],
    icon: PLATFORMS_TO_ICON[PLATFORMS.PLAYSTATION_NETWORK],
  },
  {
    value: PLATFORMS.PLAYSTATION_5,
    label: PLATFORMS_TO_LABELS[PLATFORMS.PLAYSTATION_5],
    icon: PLATFORMS_TO_ICON[PLATFORMS.PLAYSTATION_5],
  },
];

export const getPlatformLabel = (platformValue) => {
  return PLATFORMS_TO_LABELS[platformValue] || platformValue;
};

export const getPlatformIcon = (platformValue) => {
    return PLATFORMS_TO_ICON[platformValue] || faGamepad;
};