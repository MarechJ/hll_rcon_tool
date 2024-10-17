'use client';

import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@shared/components/ui/pagination';
import { Button } from '@shared/components/ui/button';
import React, { useState } from 'react';
import { Input } from '@shared/components/ui/input';
import { CheckIcon } from 'lucide-react';
import Link from 'next/link';
import { cn } from '@shared/utils';

type MatchPaginationProps = {
  page: number;
  maxPages: number;
} & React.ComponentProps<"nav">;

export default function MatchPagination({
  page,
  maxPages,
  ...props
}: MatchPaginationProps) {
  const [insertCustom, setInsertCustom] = useState(false);
  const [customPageValue, setCustomPageValue] = useState(page);

  const { className, ...rest } = props;

  const handleConfirmCustomClick = () => {
    setInsertCustom(false);
  };

  const handleCustomValueChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let pageValue = Number(e.currentTarget.value);

    if (Number.isNaN(pageValue)) {
      pageValue = page;
    }

    setCustomPageValue(
      pageValue < 1 ? 1 : pageValue > maxPages ? maxPages : pageValue
    );
  };

  return (
    <Pagination className={cn("py-2", className)} {...rest}>
      <PaginationContent>
        {page > 1 && (
          <PaginationItem>
            <PaginationPrevious href={`?page=${page - 1}`} />
          </PaginationItem>
        )}
        <PaginationItem>
          <PaginationLink isActive={page === 1} href={`?page=${1}`}>
            1
          </PaginationLink>
        </PaginationItem>
        {page === 1 && 2 < maxPages && (
          <PaginationItem>
            <PaginationLink href={`?page=${2}`}>2</PaginationLink>
          </PaginationItem>
        )}
        {page > 1 && page < maxPages && (
          <PaginationItem>
            <PaginationLink isActive={true} href={`?page=${page}`}>
              {page}
            </PaginationLink>
          </PaginationItem>
        )}
        {page !== maxPages - 1 && (
          <PaginationItem>
            {!insertCustom ? (
              <Button
                variant={'ghost'}
                size={'icon'}
                onClick={() => setInsertCustom(true)}
              >
                <PaginationEllipsis />
              </Button>
            ) : (
              <div className="flex flex-row gap-1 items-center">
                <Input
                  placeholder={'...'}
                  value={customPageValue}
                  onChange={handleCustomValueChange}
                  type="number"
                  min={1}
                  max={maxPages}
                  className="w-20"
                />
                <Button
                  variant={'outline'}
                  size={'icon'}
                  className="text-green-800 hover:text-green-600"
                  asChild
                >
                  <Link
                    href={`?page=${customPageValue}`}
                    onClick={handleConfirmCustomClick}
                  >
                    <CheckIcon size={16} />
                  </Link>
                </Button>
              </div>
            )}
          </PaginationItem>
        )}
        <PaginationItem>
          <PaginationLink
            isActive={page === maxPages}
            href={`?page=${maxPages}`}
          >
            {maxPages}
          </PaginationLink>
        </PaginationItem>
        {page < maxPages && (
          <PaginationItem>
            <PaginationNext href={`?page=${page + 1}`} />
          </PaginationItem>
        )}
      </PaginationContent>
    </Pagination>
  );
}
