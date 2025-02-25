import { cn } from '@/lib/utils'
import React, { ReactNode } from 'react'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

type MapFigureProps = {
  src: string
  name: string
  text?: string
  muted?: boolean
  gameLayout?: string[]
} & React.ComponentProps<'figure'>

export default function MapFigure({ gameLayout, src, name, text, muted, ...props }: MapFigureProps) {
  let caps = (content: ReactNode) => content;
  if (gameLayout && gameLayout.length > 0) {
    caps = (content: ReactNode) => (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>{content}</TooltipTrigger>
          <TooltipContent>
            <span>{gameLayout.join(', ')}</span>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    )
  }
  return (
    <figure className={cn('relative min-h-12', props.className)}>
      <img src={src} alt="" className={cn('w-full h-full object-cover', muted ? 'grayscale-[50]' : '')} />
      <figcaption className="absolute bottom-0 min-h-12 w-full p-1 text-center text-sm font-bold bg-background/75 group-hover:bg-background/60">
        {text && <div className="text-xs">{text}</div>}
        {caps(<div>{name}</div>)}
      </figcaption>
    </figure>
  )
}
