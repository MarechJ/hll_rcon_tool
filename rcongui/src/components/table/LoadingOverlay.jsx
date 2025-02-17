import { Stack, Skeleton } from "@mui/material";

const LoadingOverlay = () => {
  return (
    <Stack direction={"column"} spacing={1} alignItems={"center"} height={"100%"}>
      {Array.from({ length: 30 }).map((_, index) => (
        <Skeleton key={index} variant="rectangular" height={32} width={"100%"} />
      ))}
    </Stack>
  )
}

export default LoadingOverlay