import { useGlobalStore } from "@/stores/global-state";
import { ListItem, ListItemText, Stack, Tooltip } from "@mui/material";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faServer, faDesktop } from "@fortawesome/free-solid-svg-icons";
import { HIGHLIGHT } from "./utils";

const ConnectionStatus = () => {
  const backendConnected = useGlobalStore((state) => state.serverState);
  const gameConnected = useGlobalStore((state) => state.status);

  return (
    <>
      <ListItem
        sx={{
          height: 20,
          "& .MuiListItemText-root .MuiListItemText-primary": {
            fontSize: "0.75rem",
          },
        }}
      >
        <ListItemText
          sx={{ marginLeft: -0.5 }}
          primary={
            <Stack
              direction={"row"}
              justifyContent={"space-between"}
              alignItems={"center"}
            >
              <Tooltip
                enterDelay={1000}
                enterNextDelay={500}
                title={
                  gameConnected
                    ? "Successfully established connection between CRCON and HLL server"
                    : !backendConnected
                    ? "Connection between CRCON and HLL server is unknown"
                    : "CRCON is not connected to the HLL server"
                }
              >
                <Stack
                  direction={"row"}
                  justifyContent={"start"}
                  alignItems={"center"}
                  gap={0.5}
                >
                  <FontAwesomeIcon
                    icon={faServer}
                    color={
                      !gameConnected || !backendConnected
                        ? HIGHLIGHT.danger
                        : ""
                    }
                  />
                  <div>
                    {gameConnected
                      ? "Online"
                      : !backendConnected
                      ? "Unknown"
                      : "Offline"}
                  </div>
                </Stack>
              </Tooltip>
              <Tooltip
                enterDelay={1000}
                enterNextDelay={500}
                title={
                  backendConnected
                    ? "Successfully connected to CRCON."
                    : "The connection to CRCON has not been established"
                }
              >
                <Stack
                  direction={"row"}
                  justifyContent={"start"}
                  alignItems={"center"}
                  gap={0.5}
                >
                  <FontAwesomeIcon
                    icon={faDesktop}
                    color={!backendConnected ? HIGHLIGHT.danger : ""}
                  />
                  <div>{backendConnected ? "Online" : "Offline"}</div>
                </Stack>
              </Tooltip>
            </Stack>
          }
        />
      </ListItem>
    </>
  );
};

export default ConnectionStatus;
