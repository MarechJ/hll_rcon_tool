import MuiAvatar from "@mui/material/Avatar";
import MuiListItemAvatar from "@mui/material/ListItemAvatar";
import MenuItem from "@mui/material/MenuItem";
import ListItemText from "@mui/material/ListItemText";
import ListSubheader from "@mui/material/ListSubheader";
import Select, { selectClasses } from "@mui/material/Select";
import { styled } from "@mui/material/styles";
import DevicesRoundedIcon from "@mui/icons-material/DevicesRounded";
import { useGlobalStore } from "@/stores/global-state";
import { useNavigate } from 'react-router-dom';

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
  const thisServer = useGlobalStore((state) => state.serverState);
  const otherServers = useGlobalStore((state) => state.servers);
  const navigate = useNavigate();

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

  const servers = thisServer ? [thisServer, ...otherServers] : null;

  // If there's only one server, disable the selector but still show it
  // This happens when the user doesn't have permission to view other servers
  const hasOnlyOneServer = servers && servers.length === 1;

  return (
    <Select
      labelId="server-select"
      id="server-simple-select"
      value={thisServer?.server_number ?? ""}
      onChange={handleChange(servers)}
      displayEmpty
      inputProps={{ "aria-label": "Select server" }}
      fullWidth
      disabled={hasOnlyOneServer}
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
        servers.map((server) => (
          <MenuItem key={server.server_number} value={server.server_number}>
            <ListItemAvatar>
              <Avatar alt={server.name ?? "<server_name>"}>
                <DevicesRoundedIcon sx={{ fontSize: "1rem" }} />
              </Avatar>
            </ListItemAvatar>
            <ListItemText
              sx={{
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
              primary={server.name ?? "<server_name>"}
              secondary={
                `Server - ${server.server_number}` ?? "<server_number>"
              }
            />
          </MenuItem>
        ))
      ) : (
        <MenuItem value={""}>
          <ListItemAvatar>
            <Avatar alt={"?"}>
              <DevicesRoundedIcon sx={{ fontSize: "1rem" }} />
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
