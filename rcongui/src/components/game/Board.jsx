import { Typography, Divider, Stack, Box } from "@mui/material";
import { styled } from "@mui/material";
import Grid from "@mui/material/Grid2";
import { useGlobalStore } from "@/stores/global-state";

const StyledStack = styled(Stack)(({ theme }) => ({
  padding: 0,
  maxWidth: theme.breakpoints.values.md,
  margin: "0 auto",
  [theme.breakpoints.up("md")]: {
    paddingRight: theme.spacing(1),
    paddingLeft: theme.spacing(1),
  },
}));

const SmallText = styled(Typography)(({ theme }) => ({
  fontSize: theme.typography.pxToRem(12),
}));

/**
 * @typedef {Object} BoardData
 * @property {string} raw_time_remaining - The raw time remaining.
 * @property {number} allied_score - The allied score.
 * @property {number} axis_score - The axis score.
 * @property {Object} current_map - The current map.
 * @property {number} num_allied_players - The number of allied players.
 * @property {number} num_axis_players - The number of axis players.
 */

/**
 * 
 * @param {BoardData} data - The data object containing the game information.
 * @param {Object} props - Additional props.
 * @returns {JSX.Element} The rendered Board component.
 */
export const Board = ({ data, ...props }) => {
  return (
    <StyledStack>
      <SmallText textAlign={"center"} fontWeight={"bold"}>
        {data.raw_time_remaining}
      </SmallText>
      <Divider variant="middle" />
      <Grid
        container
        columnSpacing={1}
        justifyContent={"center"}
        sx={{ py: 0.5 }}
        alignContent={"center"}
      >
        <Grid
          size={4}
          sx={{
            display: "flex",
            justifyContent: "start",
            alignItems: "start",
          }}
        >
          <Box
            width={24}
            height={24}
            component={"img"}
            alt="Allies"
            src={`/icons/teams/${data.current_map.map.allies.name}.webp`}
          />
        </Grid>
        <Grid container sx={{ textAlign: "center" }} size={4}>
          <Grid size={5}>
            <Typography component={"span"} fontWeight={"bold"}>{data.allied_score}</Typography>
          </Grid>
          <Grid size={2}>
            <Typography component={"span"}>:</Typography>
          </Grid>
          <Grid size={5}>
            <Typography component={"span"} fontWeight={"bold"}>{data.axis_score}</Typography>
          </Grid>
        </Grid>
        <Grid
          size={4}
          sx={{
            display: "flex",
            justifyContent: "end",
            alignItems: "start",
          }}
        >
          <Box
            width={24}
            height={24}
            component={"img"}
            alt="Axis"
            src={`/icons/teams/${data.current_map.map.axis.name}.webp`}
          />
        </Grid>
      </Grid>
      <Divider variant="middle" />
      <Grid container>
        <Grid size={3}>
          <SmallText textAlign={"left"} sx={{ pl: 0.75 }}>
            {`[${data.num_allied_players ?? 0}]`}
          </SmallText>
        </Grid>
        <Grid size={6}>
          <SmallText textAlign={"center"}>
            {data.current_map.map.pretty_name}
          </SmallText>
        </Grid>
        <Grid size={3}>
          <SmallText textAlign={"right"} sx={{ pr: 0.75 }}>
            {`[${data.num_axis_players ?? 0}]`}
          </SmallText>
        </Grid>
      </Grid>
        <Grid size={12}>
          <SmallText textAlign={"center"}>
            {data.current_map.game_mode.toUpperCase()}
          </SmallText>
        </Grid>
    </StyledStack>
  );
};
