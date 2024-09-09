import { ExpirationField } from '../../form/custom/ExpirationField';
import { ForwardField } from '../../form/custom/ForwardField';
import { Stack } from '@mui/material';

export const AddVipFormFields = ({ control, errors }) => {
  return (
    <Stack gap={3}>
      <ForwardField control={control} errors={errors} />
      <ExpirationField control={control} errors={errors} />
      {/* <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'start',
            maxWidth: '300px',
            '& > *': { width: '100%' },
          }}
        >
          <ButtonGroup
            variant="text"
            size="small"
            aria-label="Manage hours button group"
          >
            <Button
              onClick={handleRelativeChange(-hour)}
              color="error"
              aria-label="increase 1 hour"
            >
              -
            </Button>
            <Button
              onClick={handleStaticChange(hour)}
              sx={{ flexGrow: 1 }}
              aria-label="set 1 hour"
            >
              Hour
            </Button>
            <Button
              onClick={handleRelativeChange(hour)}
              color="success"
              aria-label="decrese 1 hour"
            >
              +
            </Button>
          </ButtonGroup>
          <Divider />
          <ButtonGroup
            variant="text"
            size="small"
            aria-label="Manage days button group"
          >
            <Button
              onClick={handleRelativeChange(-day)}
              color="error"
              aria-label="increase 1 day"
            >
              -
            </Button>
            <Button
              onClick={handleStaticChange(day)}
              sx={{ flexGrow: 1 }}
              aria-label="set 1 day"
            >
              Day
            </Button>
            <Button
              onClick={handleRelativeChange(day)}
              color="success"
              aria-label="decrese 1 day"
            >
              +
            </Button>
          </ButtonGroup>
          <Divider />
  
          <ButtonGroup
            variant="text"
            size="small"
            aria-label="Manage weeks button group"
          >
            <Button
              onClick={handleRelativeChange(-week)}
              color="error"
              aria-label="increase 1 week"
            >
              -
            </Button>
            <Button
              onClick={handleStaticChange(week)}
              sx={{ flexGrow: 1 }}
              aria-label="set 1 week"
            >
              Week
            </Button>
            <Button
              onClick={handleRelativeChange(week)}
              color="success"
              aria-label="decrese 1 week"
            >
              +
            </Button>
          </ButtonGroup>
        </Box> */}
    </Stack>
  );
};
