import { Skeleton, Stack } from "@mui/material";

export const OverviewSkeleton = () => {
  return (
    <Stack sx={{ height: 180 }} spacing={2}>
      <Stack direction="row" spacing={2}>
        <Skeleton variant="rectangular" height={40} width={"20%"} />
        <Skeleton variant="rectangular" height={40} width={"20%"} />
        <Skeleton variant="rectangular" height={40} width={"20%"} />
        <Skeleton variant="rectangular" height={40} width={"20%"} />
        <Skeleton variant="rectangular" height={40} width={"20%"} />
      </Stack>
      <Stack direction="row" spacing={2} alignItems="center">
        <Skeleton variant="circular" height={50} width={50} />
        <Skeleton variant="rectangular" height={30} sx={{ flexGrow: 1 }} />
        <Skeleton variant="rectangular" height={100} width={100} />
        <Skeleton variant="rectangular" height={30} sx={{ flexGrow: 1 }} />
        <Skeleton variant="circular" height={50} width={50} />
      </Stack>
    </Stack>
  );
};
