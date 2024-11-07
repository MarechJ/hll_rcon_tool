import {
  Divider,
  FormControl,
  IconButton,
  Input,
  InputLabel,
  List,
  ListItem,
  ListItemText,
  Select,
  Stack,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from "@mui/material";
import Table from "@/components/table/Table";
import storageKeys from "@/config/storageKeys";
import TableConfigDrawer from "@/components/table/TableConfigDrawer";
import React, { useEffect, useState } from "react";
import { useStorageState } from "@/hooks/useStorageState";
import { DebouncedSearchInput } from "@/components/shared/DebouncedSearchInput";
import SettingsIcon from "@mui/icons-material/Settings";
import TableToolbar from "@/components/table/TableToolbar";
import { logActions as _logActions } from "@/utils/lib";
import { LogActionSelectionMenu } from "@/components/table/selection/LogActionSelectionMenu";
import { LogPlayerSelectionMenu } from "@/components/table/selection/LogPlayerSelectionMenu";
import { LogActionQuerySelectionMenu } from "@/components/table/selection/LogActionQuerySelectionMenu";
import DeleteIcon from "@mui/icons-material/Delete";
import KeyboardArrowRightIcon from "@mui/icons-material/KeyboardArrowRight";
import KeyboardArrowLeftIcon from "@mui/icons-material/KeyboardArrowLeft";
import KeyboardDoubleArrowLeftIcon from "@mui/icons-material/KeyboardDoubleArrowLeft";
import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";

const logActions = Object.entries(_logActions).reduce((acc, [name]) => {
  acc[name] = false;
  return acc;
}, {});

export default function LogsTable({
  table,
  logsViewData,
  searchParams,
  setSearchParams,
}) {
  const [tableConfigDrawerOpen, setTableConfigDrawerOpen] = useState(false);

  const [tableConfig, setTableConfig] = useStorageState(
    storageKeys.LIVE_LOGS_TABLE_CONFIG,
    {
      density: "normal",
      fontSize: "normal",
    }
  );

  const [logActionOptions, setLogActionOptions] = useState(logActions);
  const [playerOptions, setPlayerOptions] = useState({});

  const handleTableConfigClick = () => {
    // toggle config drawer
    setTableConfigDrawerOpen((prev) => !prev);
  };

  const handleClientActionFilterChange = (actionName) => {
    setLogActionOptions((prev) => ({
      ...prev,
      [actionName]: !prev[actionName],
    }));
  };

  const handleClientPlayerFilterChange = (actionName) => {
    setPlayerOptions((prev) => ({
      ...prev,
      [actionName]: !prev[actionName],
    }));
  };

  const handleQueryActionParamSelect = (action) => {
    setSearchParams((prev) => {
      const isToggled = prev.actions.includes(action);
      const actions = isToggled
        ? prev.actions.filter((aAction) => aAction !== action)
        : prev.actions.concat(action);
      return {
        ...prev,
        actions,
      };
    });
  };

  const handleQueryLimitInputBlur = (event) => {
    const [min, max] = [10, 100_000];
    const inputValue = Number(event.target.value);
    const limit = inputValue < min ? min : inputValue > max ? max : inputValue;
    setSearchParams((prev) => ({
      ...prev,
      limit,
    }));
  };

  const handleQueryInclusiveFilterChange = (e, mode) => {
    setSearchParams((prev) => ({
      ...prev,
      inclusive_filter: mode === "inclusive",
    }));
  };

  useEffect(() => {
    const incomingPlayers =
      logsViewData?.players?.reduce((acc, player) => {
        acc[player] = false;
        return acc;
      }, {}) ?? {};

    setPlayerOptions((prev) => {
      for (const [name, selected] in prev) {
        if (name in incomingPlayers) {
          incomingPlayers[name] = selected;
        }
      }
      return incomingPlayers;
    });
  }, [logsViewData.players]);

  useEffect(() => {
    const selectedActions = Object.entries(logActionOptions)
      .filter(([_, selected]) => selected)
      .map(([name]) => name);
    table.getColumn("action")?.setFilterValue(selectedActions);
  }, [logActionOptions]);

  useEffect(() => {
    const selectedActions = Object.entries(playerOptions)
      .filter(([_, selected]) => selected)
      .map(([name]) => name);
    table.getColumn("player_name_1")?.setFilterValue(selectedActions);
  }, [playerOptions]);

  return (
    <>
      <TableToolbar>
        <LogActionSelectionMenu
          actionOptions={logActionOptions}
          onActionSelect={handleClientActionFilterChange}
        />
        <LogPlayerSelectionMenu
          actionOptions={playerOptions}
          onActionSelect={handleClientPlayerFilterChange}
        />
      </TableToolbar>
      <Stack
        direction="row"
        spacing={1}
        flexWrap={"wrap"}
        sx={{
          borderRadius: 0,
          border: (theme) => `1px solid ${theme.palette.divider}`,
          borderBottom: "none",
        }}
      >
        <DebouncedSearchInput
          placeholder={"Search logs"}
          onChange={(value) => {
            table.getColumn("message")?.setFilterValue(value);
          }}
          sx={{ maxWidth: 230 }}
        />
        <Stack
          direction={"row"}
          justifyContent={"end"}
          alignItems={"center"}
          gap={0.25}
          flexGrow={1}
        >
          <IconButton
            onClick={() => table.firstPage()}
            disabled={!table.getCanPreviousPage()}
            size="small"
            sx={{ width: 20, height: 20, borderRadius: 0, p: 2 }}
          >
            <KeyboardDoubleArrowLeftIcon />
          </IconButton>
          <IconButton
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
            size="small"
            sx={{ width: 20, height: 20, borderRadius: 0, p: 2 }}
          >
            <KeyboardArrowLeftIcon />
          </IconButton>
          <span>
            <strong>
              {table.getState().pagination.pageIndex + 1} of{" "}
              {table.getPageCount().toLocaleString()}
            </strong>
          </span>
          <IconButton
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
            size="small"
            sx={{ width: 20, height: 20, borderRadius: 0, p: 2 }}
          >
            <KeyboardArrowRightIcon />
          </IconButton>
          <IconButton
            onClick={() => table.lastPage()}
            disabled={!table.getCanNextPage()}
            size="small"
            sx={{ width: 20, height: 20, borderRadius: 0, p: 2 }}
          >
            <KeyboardDoubleArrowRightIcon />
          </IconButton>
          <Divider flexItem orientation="vertical" />
          <IconButton
            size="small"
            sx={{ width: 20, height: 20, borderRadius: 0, p: 2 }}
            onClick={handleTableConfigClick}
          >
            <SettingsIcon sx={{ fontSize: 16 }} />
          </IconButton>
        </Stack>
      </Stack>
      <Table table={table} config={tableConfig} />
      <TableConfigDrawer
        table={table}
        name={"Logs"}
        open={tableConfigDrawerOpen}
        onClose={(config) => {
          setTableConfigDrawerOpen(false);
          setTableConfig(config);
        }}
        config={tableConfig}
      >
        <Typography sx={{ fontWeight: 500 }}>
          {"Persistent Logs Query Params"}
        </Typography>
        <Divider flexItem />
        <div>
          <Typography
            sx={{
              mb: 1,
              fontSize: "0.85rem",
              textTransform: "uppercase",
              letterSpacing: 1.5,
            }}
          >
            Filter Mode
          </Typography>
          <ToggleButtonGroup
            value={searchParams.inclusive ? "inclusive" : "exclusive"}
            exclusive
            onChange={handleQueryInclusiveFilterChange}
            aria-label="filter mode change"
            fullWidth
          >
            <ToggleButton value="inclusive" aria-label="inclusive filters">
              Inclusive
            </ToggleButton>
            <ToggleButton value="exclusive" aria-label="exclusives filters">
              Exclusive
            </ToggleButton>
          </ToggleButtonGroup>
        </div>
        <div>
          <Typography
            sx={{
              mb: 1,
              fontSize: "0.85rem",
              textTransform: "uppercase",
              letterSpacing: 1.5,
            }}
          >
            Filter Actions
          </Typography>
          <LogActionQuerySelectionMenu
            selectedActions={searchParams.actions}
            onActionSelect={handleQueryActionParamSelect}
          />
          <List dense={true} disablePadding={true}>
            {searchParams.actions.map((action, i) => (
              <React.Fragment key={action}>
                {i !== 0 && <Divider component="li" />}
                <ListItem
                  disableGutters={true}
                  secondaryAction={
                    <IconButton
                      edge="end"
                      aria-label="delete"
                      onClick={() => handleQueryActionParamSelect(action)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  }
                >
                  <ListItemText
                    primary={`${_logActions[action]} - ${action}`}
                  />
                </ListItem>
              </React.Fragment>
            ))}
            {searchParams.actions.length === 0 && (
              <ListItem disableGutters={true}>
                <ListItemText primary={"No Action Filters Selected"} />
              </ListItem>
            )}
          </List>
        </div>
        <div>
          <Typography
            sx={{
              mb: 1,
              fontSize: "0.85rem",
              textTransform: "uppercase",
              letterSpacing: 1.5,
            }}
          >
            Logs Fetch Query Limit
          </Typography>
          <TextField
            fullWidth
            defaultValue={searchParams.limit}
            onBlur={handleQueryLimitInputBlur}
            placeholder="Query limit"
            type="number"
            size="small"
          />
        </div>
      </TableConfigDrawer>
    </>
  );
}
