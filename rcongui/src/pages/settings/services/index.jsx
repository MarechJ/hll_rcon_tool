import {
  Button,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  AccordionActions,
  Chip,
  Stack,
  Alert,
  Divider,
  AlertTitle,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { cmd } from "@/utils/fetchUtils";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import localizedFormat from "dayjs/plugin/localizedFormat";
import { Form, useLoaderData } from "react-router-dom";

dayjs.extend(relativeTime);
dayjs.extend(localizedFormat);

export const loader = async () => {
  const services = await cmd.GET_SERVICES();
  return services.map((service) => ({
    ...service,
    uptime: dayjs(service.start * 1000).from(service.now * 1000),
    title: service.name.replaceAll("_", " ").toUpperCase(),
    start: dayjs(service.start * 1000).format("LLL"),
    stop: dayjs(service.stop * 1000).format("LLL"),
    now: dayjs(service.now * 1000).format("LLL"),
  }));
};

export const action = async ({ request }) => {
  const formData = Object.fromEntries(await request.formData());
  const data = await cmd.TOGGLE_SERVICE({ payload: formData });
  return data;
};

const stateColor = {
  RUNNING: "success",
  STOPPED: "default",
  FATAL: "error",
  EXITED: "info",
};

const isRunning = (service) => service.statename === "RUNNING";

const Services = () => {
  const services = useLoaderData();

  return (
    <Stack sx={{ maxWidth: (theme) => theme.breakpoints.values.md }}>
      <Alert
        sx={{ mb: 2 }}
        severity="info"
        action={
          <Button href="/api/logs" component={"a"}>
            Search logs
          </Button>
        }
      >
        Each service generates logs. If you need to report an issue, please
        include the relevant log report.
      </Alert>
      {services.map((service) => {
        return (
          <Accordion key={service.name}>
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
              aria-controls={`${service.name}-content`}
              id={`${service.name}-header`}
            >
              <Stack direction={"row"} gap={1} sx={{ minWidth: 300 }}>
                <Chip
                  sx={{ flexBasis: 80 }}
                  color={stateColor[service.statename]}
                  label={service.statename}
                />
                <Typography>{service.title}</Typography>
              </Stack>
            </AccordionSummary>

            <AccordionDetails>
              <Stack component={"section"} gap={4}>
                {service.spawnerr && (
                  <Alert severity="error">
                    <AlertTitle>Error</AlertTitle>
                    {service.spawnerr}
                  </Alert>
                )}
                <Stack
                  direction={"row"}
                  alignItems={"center"}
                  flexWrap={true}
                  gap={1}
                >
                  <Typography variant="caption">
                    {`${isRunning(service) ? "Started" : "Stopped"} ${
                      service.uptime
                    }`}
                  </Typography>
                  <Divider orientation="vertical" flexItem />
                  <Typography variant="caption">
                    Stopped @ {service.stop}
                  </Typography>
                  <Divider orientation="vertical" flexItem />
                  <Typography variant="caption">
                    Started @ {service.start}
                  </Typography>
                </Stack>
              </Stack>
              <Divider sx={{ my: 0.5 }} orientation="horizontal" flexItem />
              <Typography>
                {service.info || "Service description missing."}
              </Typography>
            </AccordionDetails>

            <AccordionActions>
              <Form method="POST">
                <input
                  name={"service_name"}
                  value={service.name}
                  hidden
                  readOnly
                />
                <Button
                  type="submit"
                  variant="contained"
                  color={isRunning(service) ? "secondary" : "primary"}
                  name={"action"}
                  value={isRunning(service) ? "stop" : "start"}
                >
                  {isRunning(service) ? "Stop service" : "Start service"}
                </Button>
              </Form>
            </AccordionActions>
          </Accordion>
        );
      })}
    </Stack>
  );
};

export default Services;
