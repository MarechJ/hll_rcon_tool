import { Typography } from "@mui/material";
import MapRotationSettings from "./map-rotation-config";
import MapRotation from "./map-rotation-list";
import { styled } from '@mui/material/styles';

const Title = styled(Typography)(({ theme }) => ({
  marginTop: theme.spacing(2),
  marginBottom: theme.spacing(2),
  borderBottom: "1px solid",
  borderColor: theme.palette.divider,
}));

function MapRotationConfig() {

  return (
    <>
      <MapRotation />
      <Title variant="h6">
        Other settings
      </Title>
      <MapRotationSettings />
    </>
  );
}

export default MapRotationConfig;
