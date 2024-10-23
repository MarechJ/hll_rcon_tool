import React from 'react';
import { DataGrid, useGridApiRef } from '@mui/x-data-grid';
import { TableToolbar } from './TableToolbar';
import { usePlayerSidebar } from '@/hooks/usePlayerSidebar';
import { NoRowsOverlay } from '@/components/NoRowsOverlay';


export const playerToRow = (player) => ({
  ...player,
  sessions_count: player?.profile?.sessions_count,
  current_playtime_seconds: player?.profile?.current_playtime_seconds,
  kicked_times: player?.profile?.penalty_count?.KICK,
  punish_times: player?.profile?.penalty_count?.PUNISH,
  tempban_times: player?.profile?.penalty_count?.TEMPBAN,
  permaban_times: player?.profile?.penalty_count?.PERMABAN,
  flags: player?.profile?.flags,
  is_watched: player?.profile?.watchlist?.is_watched,
});

const PlayersTable = ({ data: teamData, rows, columns, ...props }) => {
  const { openWithId, switchPlayer } = usePlayerSidebar();

  const apiRef = useGridApiRef();

  const tableProps = React.useMemo(
    () => ({
      getRowId: (row) => row.player_id,
      checkboxSelection: true,
      autoHeight: true,
      initialState: {
        sorting: {
          sortModel: [{ field: 'current_playtime_seconds', sort: 'desc' }],
        },
        density: 'compact',
      },
      disableRowSelectionOnClick: true,
      disableColumnMenu: true,
      slots: {
        toolbar: TableToolbar,
        noRowsOverlay: NoRowsOverlay,
      },
      sx: { '--DataGrid-overlayHeight': '300px', maxWidth: 'calc(var(--DataGrid-columnsTotalWidth) + 50px)' },
      onRowDoubleClick: (params) => {
        openWithId(params.row.player_id);
      },
      onRowClick: (params) => {
        switchPlayer(params.row.player_id);
      },
      onCellClick: (params) => {
        if (params.field !== 'assignment' && params.field !== 'unit_name')
          return;
        const squadPlayers =
          teamData.result?.[params.row.team]?.squads[params.row.unit_name]
            ?.players;
        const selectOrUnselect = !apiRef.current.isRowSelected(params.id);
        squadPlayers?.forEach((player) =>
          apiRef.current.selectRow(player.player_id, selectOrUnselect)
        );
      },
    }),
    [teamData]
  );

  return (
    <DataGrid
      columns={columns}
      rows={rows}
      apiRef={apiRef}
      columnBufferPx={350}
      disableVirtualization={false}
      {...tableProps}
      {...props}
    />
  );
};

export default PlayersTable;
