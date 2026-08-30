import {
  Button,
  Divider,
  Stack,
  Typography,
} from "@mui/material";
import {
  QueryClient,
  dehydrate,
  HydrationBoundary,
  useQuery,
} from "@tanstack/react-query";
import { useLoaderData } from "react-router-dom";
import dayjs from "dayjs";
import vipColumns from "./vip-columns";
import VipTable from "./vip-table";
import VipDownload from "./VipDownload";
import VipSyncPanel from "./VipSyncPanel";
import { vipQueryOptions } from "@/queries/vip-query";
import debug from "@/utils/debug";

const logger = debug("VIP VIEW");

const readOnlyVipColumns = vipColumns.filter(
  (column) => column.id !== "select"
);

export const loader = async () => {
  const queryClient = new QueryClient();

  logger("prefetching vip list");
  queryClient.prefetchQuery(vipQueryOptions.list());

  return { dehydratedState: dehydrate(queryClient) };
};

const VipPageContent = () => {
  const {
    data,
    isLoading,
    isFetching,
    refetch,
    dataUpdatedAt,
  } = useQuery(vipQueryOptions.list());

  return (
    <Stack spacing={1} sx={{ mt: 2 }}>
      <VipSyncPanel />

      <Stack
        direction={{ xs: "column", lg: "row" }}
        spacing={1}
        alignItems="flex-start"
      >
        <Stack
          spacing={2}
          sx={{
            width: { xs: "100%", lg: "400px" },
            bgcolor: "background.paper",
            p: 2,
          }}
        >
          <Typography variant="h6">
            Gameserver VIP state
          </Typography>

          <Typography variant="body2" color="text.secondary">
            This page shows the VIPs currently reported by this
            gameserver. VIP records are managed under VIP Lists.
          </Typography>

          <Typography>
            Last updated:{" "}
            {isFetching
              ? "Updating..."
              : dataUpdatedAt
              ? dayjs(dataUpdatedAt).format("HH:mm:ss")
              : "Never"}
          </Typography>

          <Button
            variant="contained"
            color="info"
            size="small"
            onClick={() => refetch()}
            disabled={isFetching}
          >
            Refresh gameserver state
          </Button>

          <Divider flexItem />

          <Typography variant="h6">
            Download gameserver VIPs
          </Typography>
          <VipDownload />
        </Stack>

        <VipTable
          data={data}
          columns={readOnlyVipColumns}
          isLoading={isLoading}
          isFetching={isFetching}
          readOnly
        />
      </Stack>
    </Stack>
  );
};

const VipPage = () => {
  const { dehydratedState } = useLoaderData();

  return (
    <HydrationBoundary state={dehydratedState}>
      <VipPageContent />
    </HydrationBoundary>
  );
};

export default VipPage;
