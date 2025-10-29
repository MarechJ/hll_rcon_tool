import { toSnakeCase } from "@/utils/lib";
import { Box } from "@mui/material";

export const RankIcon = ({ rank, ...props }) => (
    <Box
      component={"img"}
      src={`/icons/ranks/${toSnakeCase(rank)}.webp`}
      width={16}
      height={16}
      alt={rank}
      {...props}
    />
  );
  