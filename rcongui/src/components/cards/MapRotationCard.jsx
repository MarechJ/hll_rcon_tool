import { useQuery } from "@tanstack/react-query";
import { cmd } from "@/utils/fetchUtils";
import { Divider, Stack } from "@mui/material";
import ScrollableCard from "@/components/shared/card/ScrollableCard";
import { MapDetailsCardCompact } from "@/pages/settings/maps/MapDetailsCard";

const MapRotationCard = () => {
  const { data: mapRotation = [] } = useQuery({
    queryKey: ["map-rotation"],
    queryFn: async () => await cmd.GET_MAP_ROTATION(),
  });

  return (
    <ScrollableCard sx={{ height: "100%" }} title="Map Rotation">
      <Stack divider={<Divider sx={{ my: 0.2 }} />}>
        {mapRotation.maps.map((map) => (
          <MapDetailsCardCompact key={map.id} mapLayer={map} />
        ))}
      </Stack>
    </ScrollableCard>
  );
};

export default MapRotationCard;
