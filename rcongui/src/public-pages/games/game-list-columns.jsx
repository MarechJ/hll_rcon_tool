import { mapColumn, resultColumn, startColumn, durationColumn } from "@/pages/stats/games/game-list-columns";
import { Box, Button } from "@mui/material";
import { Link } from "react-router-dom";

export const columns = [
  {
    accessorKey: "id",
    header: <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center" }}>ID</Box>,
    cell: ({ cell }) => {
      const matchId = cell.getValue();
      return (
        <Button component={Link} to={`/games/${matchId}`} variant="text">
          {matchId}
        </Button>
      );
    },
    meta: {
      variant: "short",
    },
  },
  mapColumn,
  resultColumn,
  startColumn,
  durationColumn,
];
