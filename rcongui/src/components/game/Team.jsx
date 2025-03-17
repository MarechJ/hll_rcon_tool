import Grid from "@mui/material/Grid2";
import Points, { NumberText, SquareIcon } from "./Points";
import { Box, Divider, Stack } from "@mui/material";
import { extractTeamState } from "@/utils/extractPlayers";

const teamMetrics = ["combat", "offense", "defense", "support"];

const teamStats = ["kills", "deaths", "avg_level", "med_level"];

const teamRoles = ["armycommander", "armor", "infantry", "recon"];

const roleSrc = (role) => `/icons/roles/${role}.png`;

export const TeamMobile = ({ data, align }) => {
  const team = data ?? {};
  return (
    <Stack orientation={"vertical"} sx={{ height: "100%" }}>
      <Grid container size={6} sx={{ textAlign: "center", width: "100%" }}>
        {teamMetrics.map((metric) => (
          <Grid
            key={metric}
            size={6}
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: align,
              gap: 1,
            }}
          >
            <Points
              value={team[metric]}
              type={metric}
              direction={align === "start" ? "left" : "right"}
            />
          </Grid>
        ))}
      </Grid>
      <Grid container size={6} sx={{ textAlign: "center", width: "100%" }}>
        {teamStats.map((stat) => (
          <Grid
            key={stat}
            size={6}
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: align,
              gap: 1,
            }}
          >
            <Points
              value={team[stat]}
              type={stat}
              direction={align === "start" ? "left" : "right"}
            />
          </Grid>
        ))}
      </Grid>
    </Stack>
  );
};

export const TeamDesktop = ({ data }) => {
  const team = data ?? {};

  const roleCounts = extractTeamState(team);

  roleCounts.armycommander = !!team.commander ? 1 : 0;

  const counts = teamRoles.map((role) => ({
    role,
    count: roleCounts[role],
  }));

  return (
    <Stack orientation={"vertical"} sx={{ height: "100%" }}>
      <Stack direction={"row"} spacing={1}>
        {teamMetrics.map((metric) => (
          <Stack key={metric} direction={"row"} flexBasis={1} flexGrow={1} spacing={1}>
            <Points value={team[metric]} type={metric} />
          </Stack>
        ))}
      </Stack>
      <Divider variant="middle" />
      <Stack direction={"row"} spacing={1}>
        {teamStats.map((stat) => (
          <Stack key={stat} direction={"row"} flexBasis={1} flexGrow={1} spacing={1}>
            <Points value={team[stat]} type={stat} />
          </Stack>
        ))}
      </Stack>
      <Divider variant="middle" />
      <Stack direction={"row"} spacing={1}>
        {counts.map(({ role, count }) => (
          <Stack
            key={role}
            direction={"row"}
            flexBasis={1}
            flexGrow={1}
            spacing={1}
          >
            <SquareIcon>
              <Box
                component={"img"}
                src={roleSrc(role)}
                width={16}
                height={16}
                title={role}
              />
            </SquareIcon>
            <NumberText>{count}</NumberText>
          </Stack>
        ))}
      </Stack>
    </Stack>
  );
};
