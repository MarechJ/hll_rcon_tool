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
import ActionMenu from '@/features/player-action/ActionMenu';
import { styled } from '@mui/styles';
import { playerGameActions } from '@/features/player-action/actions';

const DesktopActionMenu = styled(Stack)(({ theme }) => ({
  display: 'flex',  
  [theme.breakpoints.down('lg')]: {
    display: 'none',
  }
}))

const MobileActionMenu = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexGrow: 1,
  justifyContent: 'end',
  alignItems: 'center',
  [theme.breakpoints.up('lg')]: {
    display: 'none',
  }
}))

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
        <DesktopActionMenu direction={'row'}>
          {playerGameActions.map((action) => (
          <React.Fragment key={action.name}>
            <Divider orientation="vertical" />
            <Tooltip
              title={action.name[0].toUpperCase() + action.name.substring(1)}
            >
              <IconButton
                onClick={() => handleActionClick(players)(action)}
              >
                {action.icon}
              </IconButton>
            </Tooltip>
          </React.Fragment>
        ))}
        </DesktopActionMenu>
        <MobileActionMenu>
          <Typography sx={{ fontSize: '0.8rem', fontWeight: '500' }}>Actions</Typography>
          <ActionMenu actionList={playerGameActions} handleActionClick={handleActionClick(players)} />
        </MobileActionMenu>
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
