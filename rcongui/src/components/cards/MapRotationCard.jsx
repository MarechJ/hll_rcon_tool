import { useQuery } from "@tanstack/react-query";
import { cmd } from "@/utils/fetchUtils";
import { Divider, Stack } from "@mui/material";
import ScrollableCard from "@/components/shared/card/ScrollableCard";
import { MapDetailsCardCompact } from "@/pages/settings/maps/MapDetailsCard";
import { mapsManagerQueryKeys } from "@/pages/settings/maps/queries";

const MapRotationCard = () => {
  const { data: mapRotation } = useQuery({
    queryKey: mapsManagerQueryKeys.mapRotation,
    queryFn: cmd.GET_MAP_ROTATION,
    initialData: { maps: [], current_index: 0, next_index: 0 },
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
