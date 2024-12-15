import { useMemo, useState, useEffect } from "react";
import Box from "@mui/material/Box";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import { cmd } from "@/utils/fetchUtils";
import { useLoaderData, useSubmit } from "react-router-dom";
import {
  Button,
  Checkbox,
  Divider,
  FormControl,
  FormControlLabel,
  IconButton,
  InputLabel,
  List,
  ListItemIcon,
  MenuItem,
  Paper,
  Select,
  Stack,
  TextField,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import { SearchInput } from "@/components/shared/SearchInput";
import debounce from "lodash/debounce";
import { InputFileUpload } from "@/components/shared/InputFileUpload";
import exportFile from "@/utils/exportFile";
import { usePlayerSidebar } from "@/hooks/usePlayerSidebar";
import PlayerAutocompletion from "@/components/form/custom/PlayerAutocompletion";

const INTENT = {
  ADD_ADMIN: "add_admin",
  DELETE_ADMIN: "delete_admin",
};

export const loader = async () => {
  const admins = await cmd.GET_CONSOLE_ADMINS();
  const adminGroups = await cmd.GET_CONSOLE_ADMIN_GROUPS();
  return { admins, adminGroups };
};

export const action = async ({ request }) => {
  const admins = await request.json();
  const results = await Promise.all(
    admins.map(({ intent, admin }) => {
      let payload;
      switch (intent) {
        case INTENT.ADD_ADMIN:
          payload = {
            description: admin.name,
            player_id: admin.player_id,
            role: admin.role.toLowerCase(),
          };
          return cmd.ADD_CONSOLE_ADMIN({ payload });
        case INTENT.DELETE_ADMIN:
          payload = { player_id: admin.player_id };
          return cmd.DELETE_CONSOLE_ADMIN({ payload });
        default:
          // Return null or reject here to handle unexpected intent
          return Promise.resolve(null); // Avoid returning null in the Promise chain
      }
    })
  );
  return results;
};

const ConsoleAdminsPage = () => {
  const { admins: serverAdmins, adminGroups } = useLoaderData();

  const initialAdmin = {
    player_id: "",
    name: "",
    role: adminGroups.includes("spectator") ? "spectator" : "",
  };

  const [admins, setAdmins] = useState(serverAdmins);
  const [checked, setChecked] = useState(new Set());
  const [searched, setSearched] = useState("");
  const [newAdmin, setNewAdmin] = useState(initialAdmin);
  const { openWithId } = usePlayerSidebar();
  const submit = useSubmit();

  const filteredAdmins = useMemo(
    () =>
      admins.filter((admin) =>
        admin.name.toLowerCase().includes(searched.toLowerCase())
      ),
    [admins, searched]
  );

  const handleOpenProfile = (playerId) => {
    openWithId(playerId);
  };

  const handleToggle = (id) => () => {
    setChecked((prev) => {
      const newChecked = new Set(prev);
      if (prev.has(id)) {
        newChecked.delete(id);
      } else {
        newChecked.add(id);
      }
      return newChecked;
    });
  };

  const handleAddItem = () => {
    if (newAdmin) {
      setAdmins((prev) => [newAdmin, ...prev]);
      setNewAdmin(initialAdmin);
    }
  };

  const handleDeleteSingleItem = (id) => {
    setAdmins((prev) => prev.filter((admin) => admin.player_id !== id));
    setChecked((prev) => {
      const newChecked = new Set(prev);
      newChecked.delete(id);
      return newChecked;
    });
  };

  const handleDeleteSelectedItems = () => {
    setAdmins((prev) => prev.filter((admin) => !checked.has(admin.player_id)));
    setChecked(new Set());
  };

  const handleToggleSelectAll = (e) => {
    if (e.target.checked) {
      setChecked(new Set(filteredAdmins.map(admin => admin.player_id)));
    } else {
      setChecked(new Set());
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    const reader = new FileReader();

    reader.onload = (e) => {
      const text = e.target.result;
      const uploadData = text
        .split("\n")
        .map((row) => {
          const [id, name, role] = row.split("\t");
          if (!id || !name || !role || !adminGroups.includes(role)) {
            return null;
          }
          return {
            player_id: id,
            name,
            role,
          };
        })
        .filter((obj) => obj !== null);
      setAdmins(uploadData);
    };

    reader.readAsText(file);
  };

  const handleFileDownload = () => {
    const rows = admins.map((admin) => [
      `${admin.player_id}\t${admin.name}\t${admin.role}`,
    ]);
    exportFile(rows, "console-admins");
  };

  const submitChanges = () => {
    const payload = [];
    const currentIds = new Set(serverAdmins.map((admin) => admin.player_id));
    const newIds = new Set(admins.map((admin) => admin.player_id));

    serverAdmins.forEach((admin) => {
      if (!newIds.has(admin.player_id)) {
        payload.push({
          intent: INTENT.DELETE_ADMIN,
          admin,
        });
      }
    });

    admins.forEach((admin) => {
      if (!currentIds.has(admin.player_id)) {
        payload.push({
          intent: INTENT.ADD_ADMIN,
          admin,
        });
      }
    });

    submit(payload, { method: "POST", encType: "application/json" });
  };

  const onSearchedChange = debounce((event) => {
    setSearched(event.target.value);
  }, 500);

  const handleInputChange = (event) => {
    const name = event.target.name;
    const value = event.target.value;
    setNewAdmin((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  useEffect(() => {
    setAdmins(serverAdmins);
  }, [serverAdmins]);

  const isValidAdminInput = useMemo(
    () => Object.entries(newAdmin).every(([_, value]) => !!value.trim()),
    [newAdmin]
  );

  const hasChanges = useMemo(() => {
    if (serverAdmins.length !== admins.length) {
      return true;
    }

    const idsCount = serverAdmins.length;
    const uniqueIds = new Set(
      serverAdmins
        .map((admin) => admin.player_id)
        .concat(admins.map((admin) => admin.player_id))
    );

    return idsCount !== uniqueIds.size;
  }, [serverAdmins, admins]);

  return (
    <Box
      sx={{
        maxWidth: (theme) => theme.breakpoints.values.md,
      }}
    >
      <Stack
        component={Paper}
        direction={"row"}
        sx={{ p: 1, mb: 1 }}
        justifyContent={"end"}
        alignItems={"center"}
        gap={1}
      >
        <InputFileUpload
          text={"Upload"}
          color={"secondary"}
          onChange={handleFileUpload}
          accept={".txt"}
        />
        <Button
          onClick={handleFileDownload}
          variant="contained"
          color="secondary"
        >
          Download
        </Button>
        <Button
          onClick={submitChanges}
          disabled={!hasChanges}
          variant="contained"
        >
          Apply
        </Button>
      </Stack>
      <Stack
        direction={"column"}
        gap={1}
        sx={{
          width: "100%",
          bgcolor: "background.paper",
          padding: 1,
        }}
      >
        <Stack direction={"row"} gap={1} sx={{ mb: 1, p: 0.5 }}>
          <PlayerAutocompletion state={newAdmin} setState={setNewAdmin}/>
          <TextField
            autoComplete={"off"}
            value={newAdmin.player_id}
            onChange={handleInputChange}
            name={"player_id"}
            fullWidth
            label={"ID"}
          />
          <FormControl fullWidth>
            <InputLabel id="admin-role-input">Role</InputLabel>
            <Select
              labelId="admin-role-input"
              id="admin-role"
              value={newAdmin.role}
              label="Role"
              name={"role"}
              onChange={handleInputChange}
            >
              {adminGroups.map((group) => (
                <MenuItem key={group} value={group}>
                  {group.toUpperCase()}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Button
            onClick={handleAddItem}
            disabled={!isValidAdminInput}
            variant="contained"
          >
            Add
          </Button>
        </Stack>
        <Stack
          direction={"row"}
          alignItems={"center"}
          justifyContent={"space-between"}
          gap={1}
          sx={{ mb: 1, p: 0.5 }}
        >
          <FormControlLabel
            sx={{ px: 0.25 }}
            label="Select"
            control={
              <Checkbox
                sx={{ mr: 1, "& .MuiSvgIcon-root": { fontSize: 16 } }}
                checked={
                  checked.size === filteredAdmins.length && checked.size !== 0
                }
                indeterminate={
                  checked.size > 0 && checked.size !== filteredAdmins.length
                }
                size="small"
                onChange={handleToggleSelectAll}
              />
            }
          />
          <Divider orientation="vertical" flexItem />
          <SearchInput
            onChange={onSearchedChange}
            placeholder="Search console admin"
          />
          <Divider orientation="vertical" flexItem />
          <Button
            onClick={handleDeleteSelectedItems}
            variant="contained"
            color="warning"
            disabled={!checked.size}
            sx={{ minWidth: "fit-content" }}
          >
            Delete selected
          </Button>
        </Stack>
        <Divider orientation="horizontal" />
        <List
          dense={true}
          sx={{
            position: "relative",
            overflow: "auto",
            maxHeight: 600,
            "& ul": { padding: 0 },
          }}
        >
          {filteredAdmins.map((admin, index) => {
            const labelId = `checkbox-list-label-${index}`;
            return (
              <ListItem
                key={admin.player_id + index}
                disablePadding
                secondaryAction={
                  <Stack direction={"row"} gap={1}>
                    <IconButton
                      onClick={() => handleOpenProfile(admin.player_id)}
                    >
                      <AccountCircleIcon />
                    </IconButton>
                    <IconButton
                      onClick={() => handleDeleteSingleItem(admin.player_id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Stack>
                }
              >
                <ListItemButton
                  role={undefined}
                  onClick={handleToggle(admin.player_id)}
                  dense
                >
                  <ListItemIcon>
                    <Checkbox
                      edge="start"
                      checked={checked.has(admin.player_id)}
                      tabIndex={-1}
                      disableRipple
                      inputProps={{ "aria-labelledby": labelId }}
                    />
                  </ListItemIcon>
                  <ListItemText
                    id={labelId}
                    primary={admin.name}
                    secondary={admin.role}
                  />
                </ListItemButton>
              </ListItem>
            );
          })}
        </List>
      </Stack>
    </Box>
  );
};

export default ConsoleAdminsPage;
