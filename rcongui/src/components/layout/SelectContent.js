import MuiAvatar from "@mui/material/Avatar";
import MuiListItemAvatar from "@mui/material/ListItemAvatar";
import MenuItem from "@mui/material/MenuItem";
import ListItemText from "@mui/material/ListItemText";
import ListSubheader from "@mui/material/ListSubheader";
import Select, { selectClasses } from "@mui/material/Select";
import { styled } from "@mui/material/styles";
import { useGlobalStore } from "@/stores/global-state";
import { useNavigate } from 'react-router-dom';
import { Skeleton } from "@mui/material";

const Avatar = styled(MuiAvatar)(({ theme }) => ({
  width: 28,
  height: 28,
  backgroundColor: theme.palette.background.paper,
  color: theme.palette.text.secondary,
  border: `1px solid ${theme.palette.divider}`,
}));

const ListItemAvatar = styled(MuiListItemAvatar)({
  minWidth: 0,
  marginRight: 12,
});

export default function SelectContent() {
  const servers = useGlobalStore((state) => state.servers);
  const thisServer = servers.find(s => s.this_server)
  const navigate = useNavigate();
  const games = {
    hll: "HLL:WW2",
    hllv: "HLL: VIETNAM",
  }

  const handleChange = (servers) => (event) => {
    const serverNumber = Number(event.target.value);
    const selectedServer = servers.find(
      (server) => server.server_number === serverNumber
    );
    if (!selectedServer) {
      return;
    }

    let newUrl;
    if (selectedServer.link) {
      newUrl = new URL(selectedServer.link);
      newUrl.pathname = window.location.pathname;
      newUrl.search = window.location.search;
      newUrl.hash = window.location.hash;
    } else {
      const regex = /:(\d+)/gm;
      newUrl = new URL(window.location.href.replace(regex, `:${selectedServer.port}`));
    }

    if (newUrl.origin === window.location.origin) {
      navigate(newUrl.pathname + newUrl.search + newUrl.hash, { replace: true });
    } else {
      window.location.replace(newUrl.href);
    }
  };

  return (
    <Select
    labelId="server-select"
    id="server-simple-select"
    value={thisServer?.server_number ?? ""}
      onChange={handleChange(servers)}
      displayEmpty
      inputProps={{ "aria-label": "Select server" }}
      fullWidth
      MenuProps={{
        PaperProps: {
          sx: {
            "& .MuiMenuItem-root:not(:last-child)": {
              mb: 1,
            },
          },
        },
      }}
      sx={{
        maxHeight: 56,
        "&.MuiList-root": {
          p: "8px",
        },
        [`& .${selectClasses.select}`]: {
          display: "flex",
          alignItems: "center",
          gap: "2px",
          pl: 1,
        },
      }}
    >
      <ListSubheader sx={{ pt: 0 }}>Servers</ListSubheader>
      {servers ? (
        servers.sort((a, b) => (a.short_name ?? a.name).localeCompare((b.short_name ?? b.name))).map((server) => (
          <MenuItem key={server.server_number} value={server.server_number}>
            <ListItemAvatar>
              <Avatar alt={server.name ?? "<server_name>"} src={`/icons/games/${server.game}_logo.webp`} />
            </ListItemAvatar>
            <ListItemText
              sx={{
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
              primary={server.short_name ?? server.name ?? "<server_name>"}
              secondary={
                `[${server.server_number ?? "<server_number>"}] - ${games[server.game] ?? "<unknown_game>"}`
              }
            />
          </MenuItem>
        ))
      ) : (
        <MenuItem value={""}>
          <ListItemAvatar>
            <Avatar alt={"?"}>
              <Skeleton variant="circular" />
            </Avatar>
          </ListItemAvatar>
          <ListItemText
            sx={{
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
            primary={"Loading..."}
            secondary={"..."}
          />
        </MenuItem>
      )}
    </Select>
  );
}
