'use client'

import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'

import { Button } from '@/components/ui/button'

export const Header = ({ header, desc, onClick }: { header: string; desc?: string; onClick?: () => void }) => (
  <TooltipProvider>
    <Tooltip>
      <TooltipTrigger asChild>
        <Button variant='ghost' size='icon' onClick={onClick} className='border px-1 min-w-10'>
          {header}
        </Button>
      </TooltipTrigger>
      <TooltipContent>
        <span>{desc}</span>
      </TooltipContent>
    </Tooltip>
  </TooltipProvider>
)

export const IconHeader = ({ src, desc, onClick }: { src: string; desc: string; onClick: () => void }) => (
  <TooltipProvider>
    <Tooltip>
      <TooltipTrigger asChild>
        <Button size='icon' className='size-6 dark:bg-transparent dark:border' onClick={onClick}>
          <img alt={desc} src={src} width={16} height={16} />
        </Button>
      </TooltipTrigger>
      <TooltipContent>
        <span>{desc}</span>
      </TooltipContent>
    </Tooltip>
  </TooltipProvider>
)
