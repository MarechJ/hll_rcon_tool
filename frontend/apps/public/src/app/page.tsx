import React, { Suspense } from "react";
import { getQueryClient } from "../../../../shared/src/lib/get-query-client";
import { dehydrate, HydrationBoundary } from "@tanstack/react-query";
import { fetchPublicInfo, publicInfoOptions } from "../utils/queries/public-info";
import { Metadata } from "next";
import { liveGameStatsOptions } from "../utils/queries/live-game-stats";
import LiveGameStats from "./live-game-stats";
import LiveGameState from "./live-game-info";
import { liveSessionStatsOptions } from "../utils/queries/live-session-stats";

export async function generateMetadata(): Promise<Metadata> {
  const data = await fetchPublicInfo();
  const name = data?.result.name.name ?? "Hell Let Loose"
  return {
    title: `Stats - ${name}`,
  }
}

export default function Index() {
  const queryClient = getQueryClient()
  void queryClient.prefetchQuery(publicInfoOptions)
  void queryClient.prefetchQuery(liveGameStatsOptions)
  void queryClient.prefetchQuery(liveSessionStatsOptions)

  return (
    <>
      <HydrationBoundary state={dehydrate(queryClient)}>
        <Suspense fallback={<div>Loading...</div>}>
          <LiveGameState />
        </Suspense>
      </HydrationBoundary>
      <HydrationBoundary state={dehydrate(queryClient)}>
        <Suspense fallback={<div>Loading...</div>}>
          <LiveGameStats />
        </Suspense>
      </HydrationBoundary>
    </>
  );
}
