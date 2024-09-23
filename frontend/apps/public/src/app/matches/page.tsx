import { getQueryClient } from '@shared/lib/get-query-client';
import { gameQueries } from '../../utils/queries/scoreboard-maps';
import { dehydrate, HydrationBoundary } from '@tanstack/react-query';
import { Suspense } from 'react';
import MatchesList from './matches-list';
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@shared/components/ui/pagination';

type SearchParams = {
  searchParams: { page?: string; page_size?: string };
};

export default function MatchesPage({ searchParams }: SearchParams) {
  const { page, page_size } = searchParams;
  const queryClient = getQueryClient();
  void queryClient.prefetchQuery(gameQueries.list());

  return (
    <>
      <HydrationBoundary state={dehydrate(queryClient)}>
        <Suspense fallback={<div>Loading...</div>}>
          <MatchesList />
        </Suspense>
      </HydrationBoundary>
      <Pagination>
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious href="#" />
          </PaginationItem>
          <PaginationItem>
            <PaginationLink href="#">1</PaginationLink>
          </PaginationItem>
          <PaginationItem>
            <PaginationEllipsis />
          </PaginationItem>
          <PaginationItem>
            <PaginationNext href="#" />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </>
  );
}
