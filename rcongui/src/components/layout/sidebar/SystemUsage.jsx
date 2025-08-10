import { cmd } from "@/utils/fetchUtils";
import {
  ListItem,
  ListItemText,
  Tooltip,
  Stack,
  Typography,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faMicrochip,
  faHardDrive,
  faMemory,
} from "@fortawesome/free-solid-svg-icons";
import { byUsage } from "./utils";

const SystemUsage = () => {
  const { data: system, isLoading } = useQuery({
    queryKey: [{ queryIdentified: "get_system_usage" }],
    queryFn: cmd.GET_SYSTEM_USAGE,
    refetchInterval: 15 * 1000,
  });

  if (isLoading)
    return (
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
            <Stack direction={"row"} justifyContent={"space-between"}>
              <FontAwesomeIcon icon={faMicrochip} />
              <FontAwesomeIcon icon={faMemory} />
              <FontAwesomeIcon icon={faHardDrive} />
            </Stack>
          }
        />
      </ListItem>
    );

  return (
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
          <Stack direction={"row"} justifyContent={"space-between"}>
            <Tooltip
              enterDelay={500}
              enterNextDelay={500}
              title={`CPU Usage: ${system.cpu_usage.percent}% on a system with ${system.cpu_usage.cores} cores running ${system.cpu_usage.process_count} processes [CRCON environment]`}
            >
              <Stack
                direction={"row"}
                justifyContent={"start"}
                alignItems={"center"}
                gap={0.5}
              >
                <FontAwesomeIcon
                  icon={faMicrochip}
                  color={byUsage(system.cpu_usage.percent)}
                />
                <div>{`${system.cpu_usage.percent}%`}</div>
              </Stack>
            </Tooltip>
            <Tooltip
              enterDelay={500}
              enterNextDelay={500}
              title={`RAM Usage: ${system.ram_usage.percent}% (${Number(
                system.ram_usage.used
              ).toFixed(1)} used GB out of ${Number(
                system.ram_usage.total
              ).toFixed(1)} GB of total CRCON environment)`}
            >
              <Stack
                direction={"row"}
                justifyContent={"start"}
                alignItems={"center"}
                gap={0.5}
              >
                <FontAwesomeIcon
                  icon={faMemory}
                  color={byUsage(system.ram_usage.percent)}
                />
                <div>{`${system.ram_usage.percent}%`}</div>
              </Stack>
            </Tooltip>
            <Tooltip
              enterDelay={500}
              enterNextDelay={500}
              title={`Storage Usage: ${system.disk_usage.percent}% (${Number(
                system.disk_usage.used
              ).toFixed(1)} GB used out of ${Number(
                system.disk_usage.total
              ).toFixed(1)} GB of total CRCON environment)`}
            >
              <Stack
                direction={"row"}
                justifyContent={"start"}
                alignItems={"center"}
                gap={0.5}
              >
                <FontAwesomeIcon
                  icon={faHardDrive}
                  color={byUsage(system.disk_usage.percent)}
                />
                <div>{`${system.disk_usage.percent}%`}</div>
              </Stack>
            </Tooltip>
          </Stack>
        }
      />
    </ListItem>
  );
};

export default SystemUsage;
