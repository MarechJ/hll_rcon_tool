import { LinkIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'

const EXTERNAL_LINKS = [
  {
    name: 'HLL Records',
    url: (playerId: string) => `https://hllrecords.com/profiles/${playerId}`,
    image: '/icons/brands/hllrecords.png',
  },
  {
    name: 'HeLO-System',
    url: (playerId: string) => `https://helo-system.de/statistics/players/${playerId}`,
    image: '/icons/brands/helo-system.png',
  },
  {
    name: 'HLLoR',
    url: (playerId: string) => `https://hellor.pro/player/${playerId}`,
    image: '/icons/brands/hllor.webp',
  },
] as const

export function PlayerLinks({ playerId }: { playerId: string }) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button type="button" size="icon" variant="outline" title="Links" aria-label="Links">
          <LinkIcon />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {EXTERNAL_LINKS.map((link) => {
          const url = link.url(playerId)
          return (
            <DropdownMenuItem key={link.name} asChild>
              <a href={url} target="_blank" rel="noopener noreferrer">
                <img className="size-5 rounded-full" src={link.image} alt="" />
                <span>{link.name}</span>
              </a>
            </DropdownMenuItem>
          )
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
