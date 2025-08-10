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

const SystemUsage = () => {
  const { data: system, isLoading } = useQuery({
    queryKey: [{ queryIdentified: "get_system_usage" }],
    queryFn: cmd.GET_SYSTEM_USAGE,
    refetchInterval: 15 * 1000,
  });

  return (
    <Stack direction={"row"} justifyContent={"space-between"}>
      <Tooltip
        title={
          !isLoading
            ? `CPU Usage: ${system.cpu_usage.percent}% on a system with ${system.cpu_usage.cores} cores running ${system.cpu_usage.process_count} processes`
            : "Loading..."
        }
      >
        <Stack
          direction={"row"}
          justifyContent={"start"}
          alignItems={"center"}
          gap={0.5}
        >
          <FontAwesomeIcon icon={faMicrochip} />
          <div>{`${!isLoading ? system.cpu_usage.percent : "?"}%`}</div>
        </Stack>
      </Tooltip>
      <Tooltip
        title={
          !isLoading
            ? `RAM Usage: ${system.ram_usage.percent}%. Used ${Number(
                system.ram_usage.used
              ).toFixed(1)} GB out of ${Number(system.ram_usage.total).toFixed(
                1
              )} GB of total memory`
            : "Loading..."
        }
      >
        <Stack
          direction={"row"}
          justifyContent={"start"}
          alignItems={"center"}
          gap={0.5}
        >
          <FontAwesomeIcon icon={faMemory} />
          <div>{`${!isLoading ? system.ram_usage.percent : "?"}%`}</div>
        </Stack>
      </Tooltip>
      <Tooltip
        title={
          !isLoading
            ? `Storage Usage: ${system.disk_usage.percent}%. Used ${Number(
                system.disk_usage.used
              ).toFixed(1)} GB out of ${Number(system.disk_usage.total).toFixed(
                1
              )} GB of total disk space`
            : "Loading..."
        }
      >
        <Stack
          direction={"row"}
          justifyContent={"start"}
          alignItems={"center"}
          gap={0.5}
        >
          <FontAwesomeIcon icon={faHardDrive} />
          <div>{`${!isLoading ? system.disk_usage.percent : "?"}%`}</div>
        </Stack>
      </Tooltip>
    </Stack>
  );
};

export default SystemUsage;
