import { queryClient } from "@/queryClient";
import {
  blacklistQueryOptions,
  getBlacklistRecordFilters,
} from "./queries";

export async function loader({ request }) {
  const filters = getBlacklistRecordFilters(new URL(request.url).searchParams);

  await Promise.all([
    queryClient.ensureQueryData(blacklistQueryOptions.lists()),
    queryClient.ensureQueryData(blacklistQueryOptions.records(filters)),
    queryClient.ensureQueryData(blacklistQueryOptions.servers()),
  ]);

  return null;
}
