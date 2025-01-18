import React from 'react'

import { Player } from '@/types/player'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Download } from 'lucide-react'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import useGameDownload from '@/hooks/use-game-download'

interface DownloadButtonProps {
  data: Player[]
  tableId: string
}

export function DownloadButton({ data, tableId }: DownloadButtonProps) {
  const { download } = useGameDownload();

  const { t } = useTranslation('game');

  return <TooltipProvider>
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          variant="outline"
          aria-label={t('downloadTable')}
          size={'icon'}
          onClick={() => download(data, `game-table-${tableId}`)}
        >
          <Download size={20} />
        </Button>
      </TooltipTrigger>
      <TooltipContent>
        <span>{t('downloadTable')}</span>
      </TooltipContent>
    </Tooltip>
  </TooltipProvider>
}
