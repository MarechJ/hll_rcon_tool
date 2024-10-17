import {
  Stack,
  Switch,
} from '@mui/material';
import {
  Autocomplete,
  Box,
  Button,
  TextField,
  Typography,
} from '@mui/material';
import { FormCard, FormCardHeader, FormCardTitle, FormDivider, StyledFormControlLabel, Wrapper } from './cards';
import React from 'react';
import { Form, useSubmit } from 'react-router-dom';
import MapListDraggable from './MapListDraggable';

export const MapRotation = ({ maps, rotation: originalRotation, shuffleEnabled }) => {
  const [rotation, setRotation] = React.useState(originalRotation);
  const submit = useSubmit();

  const removeFromRotation = (index) => {
    setRotation((rotation) => rotation.filter((item, i) => i !== index));
  };

  const addToRotation = (event, mapName) => {
    setRotation((rotation) => [mapName, ...rotation]);
  };

  const resetChanges = () => {
    setRotation(originalRotation);
  };

  const onSubmit = () => {
    const formData = new FormData();
    formData.append('rotation', JSON.stringify(rotation));
    formData.append('intent', 'do_set_map_rotation');
    submit(formData, { method: 'post' });
  };

  const options = maps;

  return (
    <Wrapper>
      <Form onSubmit={onSubmit}>
        <Stack gap={1}>
          <FormCard fullWidth>
            <Stack
              direction="row"
              gap={1}
              alignItems={'center'}
              flexWrap={'wrap'}
            >
              <Typography variant="h6">Map Rotation</Typography>
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
                value="do_set_map_rotation"
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
            disableCloseOnSelect
              onChange={addToRotation}
              disablePortal
              id="combo-box-demo"
              sx={{ flexGrow: 1 }}
              options={options}
              disableClearable
              renderInput={(params) => (
                <TextField margin="normal" {...params} label="Add Map" />
              )}
            />
            <FormDivider />
            {/* TODO */}
            {/* Pass down MAP LAYERS */}
            <MapListDraggable />
          </FormCard>
          <FormCard>
            <FormCardHeader sx={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between', }}>
              <FormCardTitle>Rotation Shuffle</FormCardTitle>
              <StyledFormControlLabel
                labelPlacement="start"
                control={
                  <Switch
                    checked={shuffleEnabled}
                    name="enabled"
                  />
                }
                label={"OFF/ON"}
              />
            </FormCardHeader>
            <Typography fontStyle={'italic'}>
              This feature is implemented by the HLL Game Server. It takes your current map rotation and shuffles it.
              It is enabled by default and will reset to default when server restarts.
              We recommend to <strong>disable</strong> this feature.
            </Typography>
          </FormCard>
        </Stack>
      </Form>
    </Wrapper>
  );
};
