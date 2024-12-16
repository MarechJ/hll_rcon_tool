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
  FormControlLabel,
  IconButton,
  List,
  ListItemIcon,
  Paper,
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
import SplitButton from "@/components/shared/SplitButton";
import dayjs from "dayjs";
import relativeTimePlugin from "dayjs/plugin/relativeTime";
import localizedFormatPlugin from "dayjs/plugin/localizedFormat";
import {
  DesktopDateTimePicker,
  LocalizationProvider,
} from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { getVipExpirationStatus, getVipExpirationStatusColor } from "@/utils/lib";
import PlayerAutocompletion from "@/components/form/custom/PlayerAutocompletion";

dayjs.extend(relativeTimePlugin);
dayjs.extend(localizedFormatPlugin);

const INTENT = {
  ADD_VIP: 0,
  DELETE_VIP: 1,
  APPLY_SINGLE: 2,
  APPLY_ALL: 3,
};

export const loader = async () => {
  const vips = await cmd.GET_VIPS();
  return {
    items: vips,
  };
};

export const action = async ({ request }) => {
  const vips = await request.json();
  const results = await Promise.all(
    vips.map(({ intent, forward, vip }) => {
      let payload;
      switch (intent) {
        case INTENT.ADD_VIP:
          payload = {
            forward,
            description: vip.name,
            player_id: vip.player_id,
            expiration: vip.vip_expiration,
          };
          return cmd.ADD_VIP({ payload });
        case INTENT.DELETE_VIP:
          payload = { player_id: vip.player_id, forward };
          return cmd.DELETE_VIP({ payload });
        default:
          // Return null or reject here to handle unexpected intent
          return Promise.resolve(null); // Avoid returning null in the Promise chain
      }
    })
  );
  return results;
};

const initialAddFormData = {
  player_id: "",
  name: "",
  vip_expiration: dayjs(),
};

const VipPage = () => {
  const { items: serverItems } = useLoaderData();
  const [clientItems, setClientItems] = useState(serverItems);
  const [checked, setChecked] = useState(new Set());
  const [searched, setSearched] = useState("");
  const [addFormData, setAddFormData] = useState(initialAddFormData);
  const { openWithId } = usePlayerSidebar();
  const submit = useSubmit();

  const filteredItems = useMemo(
    () =>
      clientItems.filter((item) =>
        item.name.toLowerCase().includes(searched.toLowerCase())
      ),
    [clientItems, searched]
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
    if (addFormData) {
      setClientItems((prev) => [addFormData, ...prev]);
      setAddFormData(initialAddFormData);
    }
  };

  const handleDeleteSingleItem = (id) => {
    setClientItems((prev) => prev.filter((vip) => vip.player_id !== id));
    setChecked((prev) => {
      const newChecked = new Set(prev);
      newChecked.delete(id);
      return newChecked;
    });
  };

  const handleDeleteSelectedItems = () => {
    setClientItems((prev) => prev.filter((vip) => !checked.has(vip.player_id)));
    setChecked(new Set());
  };

  const handleToggleSelectAll = (e) => {
    if (e.target.checked) {
      setChecked(new Set(filteredItems.map((vip) => vip.player_id)));
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
          const [id, name, expiration] = row.split("\t");
          if (!id || !name || !expiration) {
            return null;
          }
          return {
            player_id: id,
            name,
            expiration,
          };
        })
        .filter((obj) => obj !== null);
      setClientItems(uploadData);
    };

    reader.readAsText(file);
  };

  const handleFileDownload = () => {
    const rows = clientItems.map((vip) => [
      `${vip.player_id}\t${vip.name}\t${vip.vip_expiration}`,
    ]);
    exportFile(rows, "vip-players");
  };

  const submitChanges = (applyIntent) => () => {
    const payload = [];
    const currentIds = new Set(serverItems.map((vip) => vip.player_id));
    const newIds = new Set(clientItems.map((vip) => vip.player_id));

    serverItems.forEach((vip) => {
      if (!newIds.has(vip.player_id)) {
        payload.push({
          intent: INTENT.DELETE_VIP,
          forward: applyIntent === INTENT.APPLY_ALL,
          vip,
        });
      }
    });

    clientItems.forEach((vip) => {
      if (!currentIds.has(vip.player_id)) {
        payload.push({
          intent: INTENT.ADD_VIP,
          forward: applyIntent === INTENT.APPLY_ALL,
          vip,
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
    setAddFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  useEffect(() => {
    setClientItems(serverItems);
  }, [serverItems]);

  const isValidAddFormInput = useMemo(
    () =>
      Object.entries(addFormData).every(
        ([_, value]) => value ?? !!value.trim()
      ),
    [addFormData]
  );

  const hasChanges = useMemo(() => {
    if (serverItems.length !== clientItems.length) {
      return true;
    }

    const idsCount = serverItems.length;
    const uniqueIds = new Set(
      serverItems
        .map((vip) => vip.player_id)
        .concat(clientItems.map((vip) => vip.player_id))
    );

    return idsCount !== uniqueIds.size;
  }, [serverItems, clientItems]);

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
        <Box>
          <SplitButton
            disabled={!hasChanges}
            options={[
              {
                name: "Apply",
                buttonProps: {
                  onClick: submitChanges(INTENT.APPLY_SINGLE),
                  disabled: !hasChanges,
                },
              },
              {
                name: "Apply all servers",
                buttonProps: {
                  onClick: submitChanges(INTENT.APPLY_ALL),
                  disabled: !hasChanges,
                },
              },
            ]}
          />
        </Box>
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
          <PlayerAutocompletion player={addFormData} setPlayer={setAddFormData}/>
          <TextField
            autoComplete={"off"}
            value={addFormData.player_id}
            onChange={handleInputChange}
            name={"player_id"}
            fullWidth
            label={"ID"}
          />
          <LocalizationProvider dateAdapter={AdapterDayjs}>
            <DesktopDateTimePicker
              name={"vip_expiration"}
              label={"Expiration"}
              format="LLL"
              value={dayjs(addFormData.vip_expiration)}
              onChange={(dayjsValue) =>
                setAddFormData((prev) => ({
                  ...prev,
                  vip_expiration: dayjsValue.format(),
                }))
              }
              sx={{ minWidth: 300 }}
            />
          </LocalizationProvider>
          <Button
            onClick={handleAddItem}
            disabled={!isValidAddFormInput}
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
                  checked.size === filteredItems.length && checked.size !== 0
                }
                indeterminate={
                  checked.size > 0 && checked.size !== filteredItems.length
                }
                size="small"
                onChange={handleToggleSelectAll}
              />
            }
          />
          <Divider orientation="vertical" flexItem />
          <SearchInput onChange={onSearchedChange} placeholder="Search VIP" />
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
          {filteredItems.map((vip, index) => {
            const labelId = `checkbox-list-label-${index}`;
            const status = getVipExpirationStatus(vip);
            const color = getVipExpirationStatusColor(status);
            return (
              <ListItem
                key={vip.player_id + index}
                disablePadding
                secondaryAction={
                  <Stack direction={"row"} gap={1}>
                    <IconButton
                      onClick={() => handleOpenProfile(vip.player_id)}
                    >
                      <AccountCircleIcon />
                    </IconButton>
                    <IconButton
                      onClick={() => handleDeleteSingleItem(vip.player_id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Stack>
                }
              >
                <ListItemButton
                  role={undefined}
                  onClick={handleToggle(vip.player_id)}
                  dense
                >
                  <ListItemIcon>
                    <Checkbox
                      edge="start"
                      checked={checked.has(vip.player_id)}
                      tabIndex={-1}
                      disableRipple
                      inputProps={{ "aria-labelledby": labelId }}
                    />
                  </ListItemIcon>
                  <ListItemText
                    id={labelId}
                    primary={vip.name}
                    secondary={status[0].toUpperCase() + status.slice(1)}
                    secondaryTypographyProps={{
                      sx: { color },
                    }}
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

export default VipPage;
