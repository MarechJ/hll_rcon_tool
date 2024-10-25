import React from 'react';
import { IconButton, Typography, Tooltip, Divider, Box, Stack } from '@mui/material';
import {
  useGridApiContext,
  GridToolbarContainer,
  GridToolbarColumnsButton,
  GridToolbarFilterButton,
  GridToolbarDensitySelector,
} from '@mui/x-data-grid';
import { useActionDialog } from '@/hooks/useActionDialog';
import { ActionMenu, ActionPanel } from '@/features/player-action/ActionMenu';
import { styled } from '@mui/styles';
import { playerGameActions } from '@/features/player-action/actions';

export const TableToolbar = () => {
  const apiRef = useGridApiContext();
  const selectedRows = apiRef.current.getSelectedRows();
  const { openDialog } = useActionDialog();

  const handleActionClick = (recipients) => (action) => {
    openDialog(action, recipients)
  };

  if (selectedRows.size) {
    const players = Array.of(...selectedRows.values());

    return (
      <GridToolbarContainer sx={{ height: '60px', px: 2, flexWrap: 'nowrap', overflowX: 'clip' }}>
        <Typography sx={{ minWidth: 'fit-content' }}>Apply to all selected</Typography>
        <ActionPanel actionList={playerGameActions} handleActionClick={handleActionClick(players)} />
      </GridToolbarContainer>
    );
  }

  return (
    <GridToolbarContainer sx={{ height: '60px', px: 2 }}>
      <Typography>Table settings</Typography>
      <Divider orientation="vertical" />
      <GridToolbarColumnsButton />
      <Divider orientation="vertical" />
      <GridToolbarFilterButton />
      <Divider orientation="vertical" />
      <GridToolbarDensitySelector />
    </GridToolbarContainer>
  );
};
