import { Box, Typography } from "@mui/material";

export const UnderConstruction = () => {
  return (
    <Box
      sx={{
        display: "grid",
        alignContent: "center",
        justifyItems: "center",
      }}
    >
      <Box sx={{ display: "flex", flexDirection: "column", gap: 4, alignItems: 'center', justifyContent: 'center' }}>
        <Typography variant="h1">Coming soon...</Typography>
        <Box component={"img"} src="/under-construction.jpg" width={450} height={300} alt="under construction" sx={{ borderRadius: 5 }} />
      </Box>
    </Box>
  );
};
