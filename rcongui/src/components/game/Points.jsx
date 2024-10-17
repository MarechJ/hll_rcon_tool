import { Avatar, Typography } from '@mui/material';
import { styled } from '@mui/styles';

export const NumberText = styled(Typography)(() => ({
  fontSize: '0.8rem',
  fontWeight: '600',
}));

const Points = ({ value, type, direction = 'left' }) => {
  if (direction === 'left') {
    return (
      <>
        <Avatar
          src={`/icons/metrics/${type}.png`}
          alt={type}
          sx={{ width: '1rem', height: '1rem' }}
        />
        <NumberText>{value ?? 0}</NumberText>
      </>
    );
  }

  if (direction === 'right') {
    return (
      <>
        <NumberText>{value ?? 0}</NumberText>
        <Avatar
          src={`/icons/metrics/${type}.png`}
          alt={type}
          sx={{ width: '1rem', height: '1rem' }}
        />
      </>
    );
  }
};

export default Points;
