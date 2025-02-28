import {
  Box,
  Checkbox,
  IconButton,
  Stack,
  styled,
  Tooltip,
  Typography,
} from "@mui/material";
import { Star, Warning } from "@mui/icons-material";
import { yellow } from "@mui/material/colors";
import dayjs from "dayjs";
import { ActionMenuButton } from "@/features/player-action/ActionMenu";
import { generatePlayerActions } from "@/features/player-action/actions";
import { CountryFlag } from "@/components/shared/CountryFlag";
import {
  getPlayerTier,
  getSteamProfileUrl,
  hasRecentWarnings,
  isSteamPlayer,
  teamToNation,
  tierColors,
} from "@/utils/lib";
import { SortableHeader, TextButton } from "@/components/table/styles";
import RemoveRedEyeIcon from "@mui/icons-material/RemoveRedEye";
import { usePlayerSidebar } from "@/hooks/usePlayerSidebar";
import CopyableText from "@/components/shared/CopyableText";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSteam } from "@fortawesome/free-brands-svg-icons";
import Emoji from "@/components/shared/Emoji";

export const Square = styled(Box)(({ theme }) => ({
  display: "flex",
  alignItems: "start",
  justifyContent: "center",
  width: "1em",
  height: "1em",
  lineHeight: "1em",
  fontWeight: "bold",
  backgroundColor: theme.palette.background.paper,
}));

const LevelColored = styled(Box, {
  shouldForwardProp: (prop) => prop !== "level",
})((styledProps) => {
  const level = styledProps.level;
  if (!level) return {};
  const tier = getPlayerTier(level);
  const color = tierColors[tier];
  return {
    color,
  };
});

const Center = styled(Box)(() => ({
  display: "grid",
  justifyItems: "center",
  alignContent: "center",
}));

const iconFontSize = "1em";
const emojiFontSize = "0.85em";

export const columns = [
  {
    id: "select",
    header: ({ table }) => (
      <Checkbox
        checked={table.getIsAllRowsSelected()}
        indeterminate={table.getIsSomePageRowsSelected()}
        onChange={table.getToggleAllRowsSelectedHandler()}
        size="small"
        sx={{
          p: 0,
        }}
      />
    ),
    cell: ({ row }) => (
      <div>
        <Checkbox
          checked={row.getIsSelected()}
          disabled={!row.getCanSelect()}
          indeterminate={row.getIsSomeSelected()}
          onChange={row.getToggleSelectedHandler()}
          size="small"
          sx={{
            p: 0,
          }}
        />
      </div>
    ),
    meta: {
      variant: "icon",
    },
  },
  {
    accessorKey: "team",
    id: "team",
    header: SortableHeader("T", "Team"),
    cell: ({ row }) => {
      return (
        <Center>
          <Square>
            <img
              src={`/icons/teams/${teamToNation(row.original.team)}.webp`}
              width={16}
              height={16}
              alt={row.original.team}
              title={row.original.team}
            />
          </Square>
        </Center>
      );
    },
    meta: {
      variant: "icon",
    },
  },
  {
    id: "unit",
    header: SortableHeader("U", "Unit"),
    accessorKey: "unit_name",
    // Group by unit name and team
    // getGroupingValue: (row) => `${row.original.unit_name ?? "-"}-${row.original.team}`,
    cell: ({ row }) => {
      return (
        <Center>
          <Square>
            {row.original.unit_name?.charAt(0)?.toUpperCase() ?? "-"}
          </Square>
        </Center>
      );
    },
    meta: {
      variant: "icon",
    },
  },
  {
    id: "role",
    header: SortableHeader("R", "Role"),
    accessorKey: "role",
    cell: ({ row }) => {
      return (
        <Center>
          <Square
            sx={{
              bgcolor: (theme) =>
                theme.palette.mode === "dark" ? "background.paper" : "#121212",
            }}
          >
            <img
              src={`/icons/roles/${row.original.role}.png`}
              width={16}
              height={16}
              alt={row.original.role}
              title={row.original.role}
            />
          </Square>
        </Center>
      );
    },
    meta: {
      variant: "icon",
    },
  },
  {
    id: "level",
    header: SortableHeader("LVL", "Level"),
    accessorKey: "level",
    aggregationFn: "mean",
    cell: ({ row }) => {
      return (
        <LevelColored level={row.original.level} sx={{ paddingLeft: "0.75em" }}>
          {row.original.level}
        </LevelColored>
      );
    },
    meta: {
      variant: "short",
    },
  },
  {
    id: "kills",
    header: SortableHeader("KILLS", "Kills"),
    accessorKey: "kills",
    cell: ({ row }) => {
      return <>{row.original.kills}</>;
    },
  },
  {
    id: "kpm",
    header: SortableHeader("KPM", "Kills/Min"),
    accessorFn: (row) => {
      const kills = row.kills;
      const playtime = row.profile.current_playtime_seconds;
      if (kills === 0 || playtime === 0) return 0;
      return Number((kills / playtime * 60));
    },
    cell: (props) => {
      return <>{props.getValue()?.toFixed(2)}</>;
    },
  },
  {
    id: "actions",
    header: <span title="Actions">🛠️</span>,
    accessorKey: "actions",
    cell: ({ row }) => {
      return (
        <ActionMenuButton
          actions={generatePlayerActions({
            multiAction: false,
            onlineAction: true,
          })}
          recipients={row.original}
          orientation="horizontal"
          disableRipple={true}
          sx={{
            width: "1em",
            height: "1em",
            fontSize: "1em",
          }}
        />
      );
    },
    meta: {
      variant: "icon",
    },
  },
  {
    id: "platform",
    header: SortableHeader("🖥️", "Platform"),
    accessorFn: (row) => (isSteamPlayer(row) ? "Steam" : "Xbox"),
    cell: ({ row }) => {
      const isSteam = isSteamPlayer(row.original)

      return isSteam ? (
        <IconButton
          LinkComponent={"a"}
          size="small"
          sx={{ fontSize: "0.75rem" }}
          href={getSteamProfileUrl(row.original.player_id)}
          target="_blank"
          rel="noopener noreferrer"
        >
          <FontAwesomeIcon icon={faSteam} />
        </IconButton>
      ) : null;
    },
  },
  {
    id: "name",
    header: SortableHeader("Name", "Name"),
    accessorKey: "name",
    cell: ({ row }) => {
      const { openWithId } = usePlayerSidebar();
      return (
        <Stack sx={{ textAlign: "left" }}>
          <TextButton onClick={() => openWithId(row.original.player_id)}>
            {row.original.name}
          </TextButton>
          <CopyableText
            text={row.original.player_id}
            size={"0.75em"}
            sx={{
              color: "text.secondary",
              '[data-expanded-view="false"] &': {
                display: "none",
              },
            }}
          />
        </Stack>
      );
    },
  },
  {
    id: "player_id",
    header: SortableHeader("ID"),
    accessorKey: "player_id",
    cell: ({ row }) => {
      return <CopyableText text={row.original.player_id} />;
    },
  },
  {
    id: "warnings",
    header: SortableHeader("⚠️", "Has recently received action"),
    accessorKey: "profile.received_actions",
    cell: ({ row }) => {
      return hasRecentWarnings(row.original.profile.received_actions) ? (
        <Warning
          sx={{
            color: (theme) =>
              theme.palette.mode === "dark" ? yellow["500"] : "inherit",
            fontSize: iconFontSize,
          }}
        />
      ) : null;
    },
    meta: {
      variant: "icon",
    },
  },
  {
    id: "watchlist",
    header: SortableHeader("👁️", "On watchlist"),
    accessorKey: "profile.watchlist",
    cell: ({ row }) => {
      return row.original.profile?.watchlist &&
        row.original.profile?.watchlist?.is_watched ? (
        <RemoveRedEyeIcon sx={{ fontSize: iconFontSize }} />
      ) : null;
    },
  },
  {
    id: "country",
    header: SortableHeader("🌎", "Country"),
    accessorKey: "country",
    cell: ({ row }) => {
      return row.original.country && row.original.country !== "private" ? (
        <CountryFlag country={row.original.country} />
      ) : null;
    },
  },
  {
    id: "vip",
    header: SortableHeader("VIP"),
    accessorKey: "is_vip",
    cell: ({ row }) => {
      return row.original.is_vip ? (
        <Star
          sx={{
            color: (theme) =>
              theme.palette.mode === "dark" ? yellow["500"] : "inherit",
            fontSize: iconFontSize,
          }}
        />
      ) : null;
    },
  },
  {
    id: "flags",
    header: "FLAGS",
    accessorKey: "profile.flags",
    cell: ({ row }) => {
      const flags = row.original.profile.flags;
      if (!flags || flags.length === 0) return null;
      const flagsCount = 5;
      return (
        <Stack spacing={0.5} direction={"row"} alignItems={"center"}>
          {flags.slice(0, flagsCount).map(({ flag, comment: note, modified }) => (
            <Tooltip title={note} key={modified}>
              <Emoji emoji={flag} size={14} />
            </Tooltip>
          ))}
          {flags.length - flagsCount > 0 ? (
            <Typography
              variant="caption"
              sx={{ pr: 0.5, fontSize: emojiFontSize }}
            >{`+${flags.length - flagsCount}`}</Typography>
          ) : null}
        </Stack>
      );
    },
  },
  {
    id: "visits",
    header: SortableHeader("VISITS","Number of player visits"),
    accessorKey: "profile.sessions_count",
    cell: ({ row }) => {
      return <>{row.original.profile.sessions_count}</>;
    },
  },
  {
    id: "time",
    header: SortableHeader("TIME","Current Playtime"),
    accessorKey: "profile.current_playtime_seconds",
    aggregationFn: "mean",
    cell: ({ row }) => {
      return (
        <>
          {dayjs
            .duration(row.original.profile.current_playtime_seconds, "seconds")
            .format("H:mm")}
        </>
      );
    },
    meta: {
      variant: "short",
    },
  },
];