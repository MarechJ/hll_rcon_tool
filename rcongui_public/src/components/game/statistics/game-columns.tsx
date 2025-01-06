'use client'

import {Column, ColumnDef } from '@tanstack/react-table'
import { Player, PlayerTeamAssociation, PlayerWithStatus, TeamEnum } from '@/types/player'
import {IconHeader as Header} from './column-header'
import {Status} from './player-status'
import {isPlayerWithStatus} from './player/utils'
import {Button} from '@/components/ui/button'
import {useTranslation} from 'react-i18next'
import {TeamIndicator} from '@/components/game/statistics/team-indicator'
import {WeaponTypeBar} from "@/components/game/statistics/weapon-type-bar";
import {getTeamFromAssociation} from "@/components/game/statistics/utils";

const threeDigitsWidth = 40
const fourDigitsWidth = 50

export type extraColumns = 'kpm' | 'dpm';

function SortableHeader({ column, desc }: { column: Column<Player>; desc: string }) {
  return (
    <div className="text-right">
      <Button
        variant={'text'}
        onClick={() => {
          column.toggleSorting(column.getIsSorted() !== 'desc')
        }}
        className="px-0"
      >
        {desc}
      </Button>
    </div>
  )
}

const kpmColumn: ColumnDef<Player | PlayerWithStatus> = {
  accessorKey: 'kills_per_minute',
  header: function KpmHeader({ column }) {
    const { t } = useTranslation('game')
    return <SortableHeader column={column} desc={t('playersTable.killsPerMinute')} />
  },
  size: 20,
}

const dpmColumn: ColumnDef<Player | PlayerWithStatus> = {
  accessorKey: 'deaths_per_minute',
  header: function KpmHeader({ column }) {
    const { t } = useTranslation('game')
    return <SortableHeader column={column} desc={t('playersTable.deathsPerMinute')} />
  },
  size: 20,
}

function pointColumns(extras: extraColumns[]): ColumnDef<Player | PlayerWithStatus>[] {
  const c: ColumnDef<Player | PlayerWithStatus>[] = [
    {
      accessorKey: 'kills',
      size: threeDigitsWidth,
      header: function KillsHeader({ column }) {
        const { t } = useTranslation('game')
        return (
          <Header
            src={'/roles/infantry.png'}
            desc={t('playersTable.kills')}
            className={"text-right"}
            onClick={() => {
              column.toggleSorting(column.getIsSorted() !== 'desc')
            }}
          />
        )
      },
    },
  ];
  if (extras.includes('kpm')) {
    c.push(kpmColumn);
  }
  c.push({
      accessorKey: 'deaths',
      size: fourDigitsWidth,
      header: function DeathsHeader({ column }) {
        const { t } = useTranslation('game')
        return (
          <Header
            src={'/roles/medic.png'}
            desc={t('playersTable.deaths')}
            className={"text-right"}
            onClick={() => {
              column.toggleSorting(column.getIsSorted() !== 'desc')
            }}
          />
        )
      },
    }
  );
  if (extras.includes('dpm')) {
    c.push(dpmColumn);
  }
  c.push({
      accessorKey: 'combat',
      size: fourDigitsWidth,
      header: function CombatHeader({ column }) {
        const { t } = useTranslation('game')
        return (
          <Header
            src={'/roles/score_combat.png'}
            desc={t('playersTable.combat')}
            className={"text-right"}
            onClick={() => {
              column.toggleSorting(column.getIsSorted() !== 'desc')
            }}
          />
        )
      },
    },
    {
      accessorKey: 'offense',
      size: fourDigitsWidth,
      header: function OffenseHeader({ column }) {
        const { t } = useTranslation('game')
        return (
          <Header
            src={'/roles/score_offensive.png'}
            desc={t('playersTable.offense')}
            className={"text-right"}
            onClick={() => {
              column.toggleSorting(column.getIsSorted() !== 'desc')
            }}
          />
        )
      },
    },
    {
      accessorKey: 'defense',
      size: fourDigitsWidth,
      header: function DefenseHeader({ column }) {
        const { t } = useTranslation('game')
        return (
          <Header
            src={'/roles/score_defensive.png'}
            desc={t('playersTable.defense')}
            className={"text-right"}
            onClick={() => {
              column.toggleSorting(column.getIsSorted() !== 'desc')
            }}
          />
        )
      },
    },
    {
      accessorKey: 'support',
      size: fourDigitsWidth,
      header: function SupportHeader({ column }) {
        const { t } = useTranslation('game')
        return (
          <Header
            src={'/roles/score_support.png'}
            desc={t('playersTable.support')}
            className={"text-right"}
            onClick={() => {
              column.toggleSorting(column.getIsSorted() !== 'desc')
            }}
          />
        )
      },
    },
  );
  return c;
}

const playerColumn = (handlePlayerClick: (id: string) => void): ColumnDef<Player | PlayerWithStatus> => ({
  accessorKey: 'player',
  header: function NameHeader() {
    const { t } = useTranslation('game')
    return <div>{t('playersTable.player')}</div>
  },
  cell: ({ row }) => {
    const name = String(row.getValue('player'))
    const id = String(row.original.player_id)

    return (
      <div className="flex flex-row items-center gap-1">
        <Button
          variant={'text'}
          className="pl-0"
          onClick={() => {
            handlePlayerClick(id)
          }}
        >
          {name}
        </Button>
      </div>
    )
  },
  filterFn: (row, columnId: string, filterValue: string[]) => {
    if (filterValue === undefined || filterValue.length === 0) {
      return true
    }
    const value: string = row.getValue(columnId)
    return filterValue.some((v: string) => value.toLowerCase().includes(v.toLowerCase()))
  },
})

const teamColumn: ColumnDef<Player | PlayerWithStatus> = {
  accessorKey: 'team',
  header: function TeamHeader() {
    const { t } = useTranslation('game')
    return <div className={"text-center"}>{t('playersTable.team')}</div>
  },
  size: 20,
  filterFn: (row, columnId, filterValue) => {
    if (!filterValue || filterValue === 'all') {
      return true
    }
    const cellValue: PlayerTeamAssociation = row.getValue(columnId);
    return getTeamFromAssociation(cellValue) === filterValue;
  },
  cell: ({row}) => {
    const player = row.original;
    return <div className={"text-center"}>
      <TeamIndicator team={getTeamFromAssociation(player.team)} className="inline-block"/>
    </div>;
  },
};

const killCategoryColumn: ColumnDef<Player | PlayerWithStatus> = {
  accessorKey: 'kills_by_category',
  header: function KillCategoryHeader() {
    const {t} = useTranslation('game')
    return <div>{t('playersTable.killsByCategory')}</div>
  },
  size: 100,
  cell: ({row}) => {
    const player = row.original;
    return <WeaponTypeBar player={player}/> ;
  },
}

const statusColumn: ColumnDef<Player | PlayerWithStatus> = {
  accessorKey: 'is_online',
  meta: {
    filterVariant: 'select',
  },
  header: function StatusHeader() {
    const { t } = useTranslation('game')
    return <div className="sr-only w-4">{t('playersTable.status')}</div>
  },
  size: 20,
  filterFn: (row, columnId, filterValue) => {
    if (!filterValue || filterValue === 'all') {
      return true
    }
    const cellValue = row.getValue(columnId) ? 'online' : 'offline'
    return cellValue === filterValue
  },
  cell: ({ row }) => {
    const player = row.original
    return isPlayerWithStatus(player) ? <Status player={player} className="block" /> : null
  },
}

export const getLiveGameColumns = (handlePlayerClick: (id: string) => void, extras: extraColumns[] = []): ColumnDef<Player | PlayerWithStatus>[] => [
  statusColumn,
  playerColumn(handlePlayerClick),
  ...pointColumns(extras),
]

export const getCompletedGameColumns = (
  handlePlayerClick: (id: string) => void,
  extras: extraColumns[] = [],
): ColumnDef<Player | PlayerWithStatus>[] => [teamColumn, playerColumn(handlePlayerClick), killCategoryColumn, ...pointColumns(extras)]
