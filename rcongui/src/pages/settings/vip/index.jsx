import {
  Stack,
  Typography,
  IconButton,
  TextField,
  Button,
  CircularProgress,
  ToggleButtonGroup,
  ToggleButton,
  Divider,
} from "@mui/material";
import vipColumns from "./vip-columns";
import VipTable from "./vip-table";
import {
  QueryClient,
  useQuery,
  dehydrate,
  HydrationBoundary,
  useMutation,
} from "@tanstack/react-query";
import { vipMutationOptions, vipQueryOptions } from "@/queries/vip-query";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useLoaderData } from "react-router-dom";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import {
  DesktopDateTimePicker,
  LocalizationProvider,
} from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import dayjs from "dayjs";
import Padlock from "@/components/shared/Padlock";
import PlayerSearchField from "@/components/form/custom/PlayerSearchField";
import { queryClient } from "@/queryClient";
import ErrorIcon from "@mui/icons-material/Error";
import CheckIcon from "@mui/icons-material/Check";
import debug from "@/utils/debug";
import { VipBulkEditDialog } from "./VipBulkEditDialog";
import VipDownload from "./VipDownload";
import VipUpload from "./VipUpload";

const logger = debug("VIP VIEW");

const INDEFINITE_EXPIRATION = "3000-01-01T00:00:00+00:00";

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export const loader = async () => {
  const queryClient = new QueryClient();

  logger("prefetching vip list");
  queryClient.prefetchQuery(vipQueryOptions.list());

  return { dehydratedState: dehydrate(queryClient) };
};

const VipPageContent = () => {
  const { data, isLoading, isFetching, refetch, dataUpdatedAt } = useQuery(
    vipQueryOptions.list()
  );

  const [operationMode, setOperationMode] = useState("single");

  const forward = operationMode === "multi";
  const [PENDING, ERROR, SUCCESS, COMPLETED] = [0, 1, 2, 3];

  const { mutate: removeVip } = useMutation({
    ...vipMutationOptions.remove,
    retry: 3,
    retryDelay: 1000,
    onMutate: async (variables) => {
      logger("removeVip", "onMutate", variables);

      await queryClient.cancelQueries({
        queryKey: vipQueryOptions.list().queryKey,
      });

      const previousData = queryClient.getQueryData(
        vipQueryOptions.list().queryKey
      );

      queryClient.setQueryData(vipQueryOptions.list().queryKey, (old) => {
        return old.map((row) => {
          if (row.player_id === variables.player_id) {
            return { ...row, _state: PENDING };
          }
          return row;
        });
      });

      return { previousData };
    },
    onSuccess: async (_, variables, context) => {
      logger("removeVip", variables.player_id, "onSuccess");
      // Set the row state to SUCCESS
      await sleep(1000);
      queryClient.setQueryData(vipQueryOptions.list().queryKey, (old) => {
        return old.map((row) => {
          if (row.player_id === variables.player_id) {
            return { ...row, _state: SUCCESS };
          }
          return row;
        });
      });
    },
    onError: async (_, variables) => {
      logger("removeVip", variables.player_id, "onError");
      await sleep(1000);
      queryClient.setQueryData(vipQueryOptions.list().queryKey, (old) => {
        return old.map((row) => {
          if (row.player_id === variables.player_id) {
            return { ...row, _state: ERROR };
          }
          return row;
        });
      });
    },
    onSettled: async (_, error, variables) => {
      logger("removeVip", variables.player_id, "onSettled");
      await sleep(1000);
      if (!error) {
        // Remove the row from the data
        queryClient.setQueryData(vipQueryOptions.list().queryKey, (old) => {
          return old.filter((row) => row.player_id !== variables.player_id);
        });
      }
    },
  });

  const { mutate: addVip } = useMutation({
    ...vipMutationOptions.add,
    retry: 3,
    retryDelay: 1000,
    onMutate: async (variables) => {
      logger("addVip", variables.player_id, "onMutate");

      await queryClient.cancelQueries({
        queryKey: vipQueryOptions.list().queryKey,
      });
      const previousData = queryClient.getQueryData(
        vipQueryOptions.list().queryKey
      );

      // Update the cache optimistically
      queryClient.setQueryData(vipQueryOptions.list().queryKey, (old) => {
        if (!old) return [];

        // If no existing record was found, add the new one
        const exists = old.some((row) => row.player_id === variables.player_id);
        if (!exists) {
          logger("addVip", variables.player_id, "adding new record");
          return [
            {
              player_id: variables.player_id,
              name: variables.description,
              vip_expiration: variables.expiration,
              _state: PENDING,
            },
            ...old,
          ];
        }

        logger("addVip", variables.player_id, "updating existing record");
        return old.map((row) => {
          if (row.player_id === variables.player_id) {
            return {
              ...row,
              name: variables.description,
              vip_expiration: variables.expiration,
              _state: PENDING,
            };
          }
          return row;
        });
      });

      return { previousData };
    },
    onSuccess: async (_, variables) => {
      logger("addVip", variables.player_id, "onSuccess");
      await sleep(1000);
      // Update the cache to reflect the success state
      queryClient.setQueryData(vipQueryOptions.list().queryKey, (old) => {
        return old.map((row) => {
          if (row.player_id === variables.player_id) {
            return {
              ...row,
              _state: SUCCESS,
            };
          }
          return row;
        });
      });
    },
    onError: async (_, variables) => {
      logger("addVip", variables.player_id, "onError");
      await sleep(1000);
      // Update the cache to reflect the error state
      queryClient.setQueryData(vipQueryOptions.list().queryKey, (old) => {
        return old.map((row) => {
          if (row.player_id === variables.player_id) {
            return {
              ...row,
              _state: ERROR,
            };
          }
          return row;
        });
      });
    },
    onSettled: async (_, error, variables) => {
      logger("addVip", variables.player_id, "onSettled");
      await sleep(1000);
      if (!error) {
        // Remove the row from the data
        queryClient.setQueryData(vipQueryOptions.list().queryKey, (old) => {
          return old.map((row) => {
            if (row.player_id === variables.player_id) {
              return {
                ...row,
                _state: COMPLETED,
              };
            }
            return row;
          });
        });
      }
    },
  });

  // Form state
  const [vipIndefinitely, setVipIndefinitely] = useState(false);
  const [formFields, setFormFields] = useState({
    description: "",
    player_id: "",
    expiration: dayjs().add(5, "minutes"),
    forward,
  });
  const [searchPlayer, setSearchPlayer] = useState({ name: "", player_id: "" });

  useEffect(() => {
    if (searchPlayer.player_id) {
      handleVipEdit({
        description: searchPlayer.name,
        player_id: searchPlayer.player_id,
        expiration: dayjs().add(5, "minutes"),
      });
    }
  }, [searchPlayer.player_id]);

  const columns = useMemo(
    () => [
      ...vipColumns,
      {
        id: "actions",
        header: "Actions",
        cell: ({ row }) => {
          const state = row.original._state;
          let removeComponent = null;
          switch (state) {
            case PENDING:
              removeComponent = (
                <Stack
                  direction="row"
                  alignItems="center"
                  sx={{ padding: "5px" }}
                >
                  <CircularProgress size={20} />
                </Stack>
              );
              break;
            case SUCCESS:
              removeComponent = (
                <Stack
                  direction="row"
                  alignItems="center"
                  sx={{ padding: "5px" }}
                >
                  <CheckIcon sx={{ fontSize: "1em" }} color="success" />
                </Stack>
              );
              break;
            case ERROR:
              removeComponent = (
                <Stack
                  direction="row"
                  alignItems="center"
                  sx={{ padding: "5px" }}
                >
                  <ErrorIcon sx={{ fontSize: "1em" }} color="warning" />
                </Stack>
              );
              break;
            default:
              removeComponent = (
                <Stack direction="row" alignItems="center" spacing={1}>
                  <IconButton
                    variant="contained"
                    size="small"
                    color={"error"}
                    onClick={() =>
                      handleRemoveVip(row.original.player_id, forward)
                    }
                    disabled={isFetching}
                  >
                    <DeleteIcon sx={{ fontSize: "1em" }} />
                  </IconButton>
                </Stack>
              );
              break;
          }

          return (
            <Stack direction="row" alignItems="center" spacing={1}>
              {removeComponent}
              <IconButton
                variant="contained"
                size="small"
                color="primary"
                onClick={() => {
                  handleVipEdit({
                    description: row.original.name,
                    player_id: row.original.player_id,
                    expiration: row.original.vip_expiration,
                  });
                }}
                disabled={isFetching}
              >
                <EditIcon sx={{ fontSize: "1em" }} />
              </IconButton>
            </Stack>
          );
        },
      },
    ],
    [isFetching, forward]
  );

  const [bulkEditOpen, setBulkEditOpen] = useState(false);
  const [selectedTable, setSelectedTable] = useState(null);

  const handleEditSelected = useCallback(
    (table) => {
      setSelectedTable(table);
      setBulkEditOpen(true);
    },
    [setSelectedTable, setBulkEditOpen]
  );

  const handleBulkEdit = ({ mode, value }) => {
    const selectedIds = selectedTable
      .getSelectedRowModel()
      .rows.map((row) => row.original.player_id);

    if (mode === "set") {
      selectedIds.forEach((playerId) => {
        addVip({
          player_id: playerId,
          expiration: value,
          description:
            data.find((row) => row.player_id === playerId)?.name || "",
          forward,
        });
      });
    } else {
      // Extend mode
      selectedIds.forEach((playerId) => {
        const currentVip = data.find((row) => row.player_id === playerId);
        if (!currentVip) return;

        // If the expiration is null, we need to set it some value
        const vipExpiration =
          currentVip.vip_expiration === null
            ? INDEFINITE_EXPIRATION
            : currentVip.vip_expiration;

        // Calculate the new expiration date
        let newExpiration = dayjs(vipExpiration).add(
          value.diff(dayjs(), "millisecond")
        );

        // If the new expiration is after the indefinite expiration date, set it to null
        if (
          newExpiration.isSame(dayjs(INDEFINITE_EXPIRATION)) ||
          newExpiration.isAfter(dayjs(INDEFINITE_EXPIRATION))
        ) {
          newExpiration = null;
        }

        addVip({
          player_id: playerId,
          expiration: newExpiration,
          description: currentVip.name,
          forward,
        });
      });
    }
  };

  const handleVipEdit = ({ description, player_id, expiration }) => {
    if (!expiration || expiration === INDEFINITE_EXPIRATION) {
      setVipIndefinitely(true);
      setFormFields((prev) => ({ ...prev, description, player_id }));
    } else {
      setVipIndefinitely(false);
      setFormFields({ description, player_id, expiration: dayjs(expiration) });
    }
  };

  const handleAddVip = () => {
    logger("addVip", formFields.player_id);
    addVip({
      ...formFields,
      expiration: vipIndefinitely ? null : formFields.expiration,
    });
    handleClear();
  };

  const handleClear = () => {
    setFormFields({
      description: "",
      player_id: "",
      expiration: dayjs().add(5, "minutes"),
    });
    setVipIndefinitely(false);
  };

  const handleRemoveVip = (player_id, forward) => {
    removeVip({ player_id, forward });
  };

  const handleBulkRemove = useCallback(
    (table) => {
      const selectedPlayersIds = table
        .getSelectedRowModel()
        .rows.map((row) => row.original.player_id);
      selectedPlayersIds.forEach((player_id) => {
        removeVip({ player_id, forward });
      });
      table.setRowSelection({});
    },
    [removeVip]
  );

  const handleOperationModeChange = (newMode) => {
    setOperationMode(newMode);
    setFormFields((prev) => ({ ...prev, forward: newMode === "multi" }));
  };

  return (
    <Stack direction={{ xs: "column", lg: "row" }} spacing={1} sx={{ mt: 2 }}>
      <Stack spacing={1} sx={{ width: { xs: "100%", lg: "400px" } }}>
        <Stack spacing={2} sx={{ bgcolor: "background.paper", p: 2 }}>
          <Typography variant="h6">Apply changes to</Typography>
          <ToggleButtonGroup
            value={operationMode}
            exclusive
            onChange={(_, newMode) => {
              if (newMode !== null) {
                handleOperationModeChange(newMode);
              }
            }}
            fullWidth
            size="small"
          >
            <ToggleButton value="single" color="primary">
              This server
            </ToggleButton>
            <ToggleButton value="multi" color="primary">
              All servers
            </ToggleButton>
          </ToggleButtonGroup>
        </Stack>

        <Stack spacing={2} sx={{ bgcolor: "background.paper", p: 2 }}>
          <Typography>
            Last updated:{" "}
            {isFetching
              ? "Updating..."
              : dataUpdatedAt
              ? dayjs(dataUpdatedAt).format("HH:mm:ss")
              : "Never"}
          </Typography>
          <Button
            variant="contained"
            color="info"
            size="small"
            onClick={refetch}
            disabled={isFetching}
          >
            Refresh
          </Button>
        </Stack>
        <Stack spacing={2} sx={{ bgcolor: "background.paper", p: 2 }}>
          <Typography variant="h6">Search Player</Typography>
          <PlayerSearchField
            player={searchPlayer}
            setPlayer={setSearchPlayer}
          />
        </Stack>
        <Stack spacing={2} sx={{ bgcolor: "background.paper", p: 2 }}>
          <Typography variant="h6">Add VIP</Typography>
          <TextField
            value={formFields.description}
            onChange={(e) =>
              setFormFields({ ...formFields, description: e.target.value })
            }
            label="Player Name"
            name="description"
            fullWidth
          />
          <TextField
            value={formFields.player_id}
            onChange={(e) =>
              setFormFields({ ...formFields, player_id: e.target.value })
            }
            label="Player ID"
            name="player_id"
            fullWidth
          />
          <LocalizationProvider dateAdapter={AdapterDayjs}>
            <DesktopDateTimePicker
              value={formFields.expiration}
              onChange={(e) => setFormFields({ ...formFields, expiration: e })}
              format="LLL"
              label="Expiration"
              name="expiration"
              maxDateTime={dayjs(INDEFINITE_EXPIRATION)}
              disabled={vipIndefinitely}
              disablePast={true}
            />
          </LocalizationProvider>
          <Padlock
            checked={vipIndefinitely}
            handleChange={setVipIndefinitely}
            label="Never expires"
          />
          <Button variant="contained" color="primary" onClick={handleClear}>
            Clear
          </Button>
          <Button
            variant="contained"
            color="primary"
            disabled={isFetching}
            onClick={handleAddVip}
          >
            Add VIP
          </Button>
        </Stack>

        <Stack spacing={2} sx={{ bgcolor: "background.paper", p: 2 }}>
          <Typography variant="h6">Download VIPs</Typography>
          <VipDownload />
          <Divider flexItem orientation="horizontal" />
          <Typography variant="h6">Upload VIPs</Typography>
          <VipUpload />
        </Stack>
      </Stack>
      <VipTable
        data={data}
        columns={columns}
        isLoading={isLoading}
        isFetching={isFetching}
        handleBulkRemove={handleBulkRemove}
        editSelected={handleEditSelected}
      />
      <VipBulkEditDialog
        open={bulkEditOpen}
        onClose={() => setBulkEditOpen(false)}
        onConfirm={handleBulkEdit}
        selectedCount={selectedTable?.getSelectedRowModel().rows.length || 0}
      />
    </Stack>
  );
};

const VipPage = () => {
  const { dehydratedState } = useLoaderData();

  return (
    <HydrationBoundary state={dehydratedState}>
      <VipPageContent />
    </HydrationBoundary>
  );
};

export default VipPage;
