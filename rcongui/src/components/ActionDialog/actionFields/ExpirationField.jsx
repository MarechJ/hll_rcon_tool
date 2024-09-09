// TODO
// FOR THE FUTURE?
//
export const ExpirationField = ({ field }) => {
    const [value, setValue] = React.useState(
      field.defaultValue ? dayjs(field.defaultValue) : dayjs(new Date())
    );
  
    const hour = 1;
    const day = 24 * hour;
    const week = 7 * day;
  
    const handleRelativeChange = (hours) => () => {
      setValue(prevState => {
        const prevValue = dayjs(prevState)
        const nextValue = prevValue.add(hours, 'hour')
        return nextValue;
      })
    }
  
    const handleStaticChange = (hours) => () => {
      const now = dayjs(new Date());
      const nextValue = now.add(hours, 'hour')
      setValue(nextValue)
    }
  
    return (
      <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <DesktopDateTimePicker
            value={value}
            onChange={setValue}
            name={field.name}
            id={field.name}
            label={field.label}
            disablePast
            sx={{ maxWidth: '300px' }}
          />
        </LocalizationProvider>
        <Box
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
            <Button onClick={handleRelativeChange(-hour)} color="error" aria-label='increase 1 hour'>-</Button>
            <Button onClick={handleStaticChange(hour)} sx={{ flexGrow: 1 }} aria-label='set 1 hour'>Hour</Button>
            <Button onClick={handleRelativeChange(hour)} color="success" aria-label='decrese 1 hour'>+</Button>
          </ButtonGroup>
          <Divider />
          <ButtonGroup
            variant="text"
            size="small"
            aria-label="Manage days button group"
          >
            <Button onClick={handleRelativeChange(-day)} color="error" aria-label='increase 1 day'>-</Button>
            <Button onClick={handleStaticChange(day)} sx={{ flexGrow: 1 }} aria-label='set 1 day'>Day</Button>
            <Button onClick={handleRelativeChange(day)} color="success" aria-label='decrese 1 day'>+</Button>
          </ButtonGroup>
          <Divider />
  
          <ButtonGroup
            variant="text"
            size="small"
            aria-label="Manage weeks button group"
          >
            <Button onClick={handleRelativeChange(-week)} color="error" aria-label='increase 1 week'>-</Button>
            <Button onClick={handleStaticChange(week)} sx={{ flexGrow: 1 }} aria-label='set 1 week'>Week</Button>
            <Button onClick={handleRelativeChange(week)} color="success" aria-label='decrese 1 week'>+</Button>
          </ButtonGroup>
        </Box>
      </Paper>
    );
  };