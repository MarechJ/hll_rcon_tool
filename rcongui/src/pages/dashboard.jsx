import { useAuth } from '@/hooks/useAuth';
import { useGlobalStore } from '@/hooks/useGlobalState';
import {
  Typography,
} from '@mui/material';
import Grid from "@mui/material/Grid2"

const Dashboard = () => {
  const { permissions } = useAuth()
  const onlineCrconMods = useGlobalStore((state) => state.onlineCrconMods)
  const onlineIngameMods = useGlobalStore((state) => state.onlineIngameMods)

  return (
    <Grid container sx={{ overflow: "hidden" }}>
      <Grid
        size={{
          xs: 12,
        }}>
          <Typography variant='h1'>Welcome back, {permissions?.user_name ?? "user"}!</Typography>
          <Typography>{`Online Moderators(${onlineCrconMods?.length ?? 0}): ${onlineCrconMods?.map(mod => mod.username)?.join(',') || "None"}`}</Typography>
          <Typography>{`Online Moderators In-Game(${onlineIngameMods?.length ?? 0}): ${onlineIngameMods?.map(mod => mod.username).join(',') || "None"}`}</Typography>
      </Grid>
    </Grid>
  );
};

export default Dashboard;