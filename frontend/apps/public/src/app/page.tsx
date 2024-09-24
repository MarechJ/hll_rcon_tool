import React, { Suspense } from "react";
import { getQueryClient } from "../../../../shared/src/lib/get-query-client";
import { dehydrate, HydrationBoundary } from "@tanstack/react-query";
import { fetchPublicInfo, publicInfoOptions } from "../utils/queries/public-info";
import { Metadata } from "next";
import { liveGameStatsOptions } from "../utils/queries/live-game-stats";
import GameState from "./game-state";
import LiveGameStats from "./game-stats";

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

  return (
    <>
      <HydrationBoundary state={dehydrate(queryClient)}>
        <Suspense fallback={<div>Loading...</div>}>
          <GameState />
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