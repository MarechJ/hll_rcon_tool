import { getQueryClient } from '@shared/lib/get-query-client';
import { gameQueries } from '../../utils/queries/scoreboard-maps';
import { dehydrate, HydrationBoundary } from '@tanstack/react-query';
import { Suspense } from 'react';
import MatchesList from './matches-list';

type SearchParams = {
  searchParams: { page?: string; page_size?: string };
};

export default function MatchesPage({ searchParams }: SearchParams) {
  const { page: pageParam, page_size: pageSizeParam } = searchParams;
  const page = Number(pageParam ?? 1)
  const pageSize = Number(pageSizeParam ?? 50)
  const query = Number.isNaN(page) || Number.isNaN(pageSize) ? gameQueries.list() : gameQueries.list(page, pageSize);
  const queryClient = getQueryClient();
  void queryClient.prefetchQuery(query);

  return (
    <>
      <HydrationBoundary state={dehydrate(queryClient)}>
        <Suspense fallback={<div>Loading...</div>}>
          <MatchesList page={page} pageSize={pageSize} />
        </Suspense>
      </HydrationBoundary>
    </>
  );
}
