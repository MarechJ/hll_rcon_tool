import { IconButton, ListItem, ListItemText, Stack } from '@mui/material';
import {
  Autocomplete,
  Box,
  Button,
  List,
  TextField,
  Typography,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { difference } from 'lodash';
import { FormCard, FormDivider, Wrapper } from './cards';
import React from 'react';
import { Form, useSubmit } from 'react-router-dom';

export const VotemapMapOptions = ({ maps, whitelist }) => {
  const [whitelisted, setWhitelisted] = React.useState(whitelist);
  const submit = useSubmit();

  const removeFromWhitelist = (mapName) => {
    setWhitelisted((whitelist) => whitelist.filter((item) => item !== mapName));
  };

  const addToWhitelist = (event, mapName) => {
    setWhitelisted((whitelist) => [mapName, ...whitelist]);
  };

  const resetChanges = () => {
    setWhitelisted(whitelist);
  };

  const onSubmit = () => {
    const formData = new FormData();
    formData.append('whitelist', JSON.stringify(whitelisted))
    formData.append('intent', 'do_set_map_whitelist');
    submit(formData, { method: 'post' });
  };

  const options = difference(maps, whitelisted);
  const allOptionsUsed = !options.length;

  return (
    <Form onSubmit={onSubmit}>
      <Wrapper>
        <FormCard fullWidth>
          <Stack
            direction="row"
            gap={1}
            alignItems={'center'}
            flexWrap={'wrap'}
          >
            <Typography variant="h6">Allowed Map Options</Typography>
            <Box sx={{ flexGrow: 1 }}></Box>
            <Button
              variant="contained"
              size="small"
              color="warning"
              onClick={resetChanges}
            >
              Reset
            </Button>
            <Button
              name="intent"
              value="do_set_map_whitelist"
              variant="contained"
              type="submit"
              size="small"
            >
              Save
            </Button>
          </Stack>
        </FormCard>
        <FormCard fullWidth>
          <Autocomplete
            onChange={addToWhitelist}
            disablePortal
            id="combo-box-demo"
            sx={{ flexGrow: 1 }}
            options={options}
            disabled={allOptionsUsed}
            disableClearable
            clearOnBlur
            renderInput={(params) => (
              <TextField
                helperText={allOptionsUsed && 'All maps already selected.'}
                margin="normal"
                {...params}
                label="Add Map"
              />
            )}
          />
          <FormDivider />
          <List dense={true}>
            {whitelisted.map((mapName) => {
              return (
                <ListItem
                  divider
                  key={mapName}
                  secondaryAction={
                    <IconButton
                      size="small"
                      edge="end"
                      aria-label="delete"
                      onClick={() => removeFromWhitelist(mapName)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  }
                >
                  <ListItemText primary={mapName} />
                </ListItem>
              );
            })}
          </List>
        </FormCard>
      </Wrapper>
    </Form>
  );
};
