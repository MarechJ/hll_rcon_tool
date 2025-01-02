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
  getXboxProfileUrl,
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
import { faSteam, faXbox } from "@fortawesome/free-brands-svg-icons";
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
    header: SortableHeader("T"),
    cell: ({ row }) => {
      return (
        <Center>
          <Square>
            <img
              src={`/icons/teams/${teamToNation(row.original.team)}.webp`}
              width={16}
              height={16}
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
    header: SortableHeader("U"),
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
    header: SortableHeader("R"),
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
    header: SortableHeader("LVL"),
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
    header: SortableHeader("KILLS"),
    accessorKey: "kills",
    cell: ({ row }) => {
      return <>{row.original.kills}</>;
    },
  },
  {
    id: "kills_per_minute",
    header: SortableHeader("KPM"),
    accessorKey: "kills_per_minute",
    cell: ({ row }) => {
      return <>{Number(row.original.kills / row.original.profile.current_playtime_seconds * 60).toFixed(2)}</>;
    },
  },
  {
    id: "actions",
    header: "🛠️",
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
    header: SortableHeader("🖥️"),
    accessorFn: (row) => (isSteamPlayer(row) ? "Steam" : "Xbox"),
    cell: ({ row }) => {
      const url = isSteamPlayer(row.original)
        ? getSteamProfileUrl(row.original.player_id)
        : getXboxProfileUrl(row.original.name);
      const icon = isSteamPlayer(row.original) ? faSteam : faXbox;
      return (
        <IconButton
          LinkComponent={"a"}
          size="small"
          sx={{ fontSize: "0.75rem" }}
          href={url}
          target="_blank"
          rel="noopener noreferrer"
        >
          <FontAwesomeIcon icon={icon} />
        </IconButton>
      );
    },
  },
  {
    id: "name",
    header: SortableHeader("Name"),
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
    header: SortableHeader("⚠️"),
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
    header: SortableHeader("👁️"),
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
    header: SortableHeader("🌎"),
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
    header: SortableHeader("VISITS"),
    accessorKey: "profile.sessions_count",
    cell: ({ row }) => {
      return <>{row.original.profile.sessions_count}</>;
    },
  },
  {
    id: "time",
    header: SortableHeader("TIME"),
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
