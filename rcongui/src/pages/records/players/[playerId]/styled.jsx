import { styled } from '@mui/material/styles';
import { Paper, Box, Avatar, Chip, Card as MuiCard, Alert, Tooltip } from '@mui/material';

export const ProfileContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  maxWidth: '1400px',
  margin: '0 auto',
  backgroundColor: theme.palette.background.default,
  minHeight: '100vh',
}));

export const TopSection = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  marginBottom: theme.spacing(3),
  backgroundColor: theme.palette.background.paper,
  padding: theme.spacing(2, 3),
  borderRadius: theme.shape.borderRadius,
}));

export const PlayerInfo = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(2),
}));

export const PlayerAvatar = styled(Avatar)(({ theme }) => ({
  width: theme.spacing(6),
  height: theme.spacing(6),
  backgroundColor: theme.palette.mode === 'dark' 
    ? theme.palette.grey[800] 
    : theme.palette.grey[200],
  color: theme.palette.text.primary,
  fontSize: '1rem',
  fontWeight: 500,
}));

export const PlayerNameSection = styled(Box)({
  display: 'flex',
  alignItems: 'baseline',
  gap: '12px',
});

export const BadgesContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  gap: theme.spacing(1),
  alignItems: 'center',
}));

export const StyledChip = styled(Chip)(({ theme }) => ({
  borderRadius: theme.shape.borderRadius,
  height: 24,
  backgroundColor: theme.palette.mode === 'dark' ? '#000' : '#111',
  color: '#fff',
  fontWeight: 500,
  fontSize: '0.75rem',
  '& .MuiChip-label': {
    padding: '0 12px',
  },
  '& .MuiChip-icon': {
    color: 'inherit',
    marginLeft: 8,
  },
  '&.trusted': {
    backgroundColor: theme.palette.mode === 'dark' ? '#000' : '#111',
  },
  '&.vip': {
    backgroundColor: theme.palette.mode === 'dark' ? '#000' : '#111',
  },
  '&.admin': {
    backgroundColor: theme.palette.mode === 'dark' ? '#000' : '#111',
  },
}));

export const ActiveBanAlert = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(3),
  backgroundColor: theme.palette.error.light,
  color: theme.palette.error.dark,
  borderRadius: theme.shape.borderRadius,
  '& .MuiTypography-root': {
    color: 'inherit',
  },
}));

export const MainContent = styled(Box)(({ theme }) => ({
  display: 'grid',
  gap: theme.spacing(3),
  gridTemplateColumns: '1fr',
  [theme.breakpoints.up('md')]: {
    gridTemplateColumns: '350px 1fr',
  },
}));

export const SummaryCard = styled(MuiCard)(({ theme }) => ({

}));

export const DetailCard = styled(MuiCard)(({ theme }) => ({
  height: '100%',
  backgroundColor: theme.palette.background.paper,
  '& .MuiCardHeader-root': {
    borderBottom: `1px solid ${theme.palette.divider}`,
  },
  '& .MuiTabs-root': {
    borderBottom: `1px solid ${theme.palette.divider}`,
    '& .MuiTab-root': {
      minHeight: 48,
    },
  },
}));

export const ScrollableContent = styled(Box)(({ theme }) => ({
  height: '500px',
  overflowY: 'auto',
  marginTop: theme.spacing(2),
  padding: theme.spacing(0, 2),
}));

export const ListItem = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  '&:not(:last-child)': {
    borderBottom: `1px solid ${theme.palette.divider}`,
  },
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
  },
}));

export const FilterSection = styled(Box)(({ theme }) => ({
  display: 'flex',
  gap: theme.spacing(2),
  marginBottom: theme.spacing(2),
  padding: theme.spacing(2),
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.shape.borderRadius,
  '& .MuiTextField-root': {
    flex: 1,
  },
  '& .date-inputs': {
    display: 'flex',
    gap: theme.spacing(1),
    flex: 1,
  },
}));

export const StatItem = styled(Box)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'space-between',
  padding: theme.spacing(1.5, 0),
  '&:not(:last-child)': {
    borderBottom: `1px solid ${theme.palette.divider}`,
  },
}));

export const PenaltiesGrid = styled(Box)(({ theme }) => ({
  display: 'grid',
  gridTemplateColumns: 'repeat(2, 1fr)',
  gap: theme.spacing(1),
  marginTop: theme.spacing(1),
  padding: theme.spacing(2),
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.shape.borderRadius,
  '& .MuiTypography-root': {
    fontSize: '0.875rem',
  },
}));

export const StatusAlert = styled(Alert)(({ theme }) => ({
  marginBottom: theme.spacing(2),
  backgroundColor: 'transparent',
  '& .MuiAlert-message': {
    width: '100%',
  },
}));

export const StatusChip = styled(Chip)(({ theme }) => ({
  margin: theme.spacing(0.5),
  '&.watched': {
    backgroundColor: theme.palette.warning.light,
    color: theme.palette.warning.dark,
  },
  '&.blacklisted': {
    backgroundColor: theme.palette.error.light,
    color: theme.palette.error.dark,
  },
  '&.banned': {
    backgroundColor: theme.palette.error.main,
    color: theme.palette.common.white,
  },
}));

export const VipStatusSection = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing(1),
  padding: theme.spacing(2, 0),
  borderBottom: `1px solid ${theme.palette.divider}`,
}));

export const VipChip = styled(Chip)(({ theme }) => ({
  backgroundColor: theme.palette.warning.dark,
  color: theme.palette.common.white,
  '& .MuiChip-icon': {
    color: 'inherit',
  },
})); 