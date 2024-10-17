import React from 'react';
import {
  Box,
  Button,
  FormControl,
  FormControlLabel,
  FormGroup,
  FormLabel,
  Radio,
  RadioGroup,
  Stack,
  Switch,
  TextField,
  Typography,
} from '@mui/material';
import { Form, useActionData, useLoaderData, useSubmit } from 'react-router-dom';
import {
  FormCard,
  FormCardTitle,
  FormDivider,
  StyledFormControlLabel,
  SwitchHelperText,
  Wrapper,
} from './cards';

const FACTORY_CONFIG = {
  enabled: false,
  default_method: 'least_played_from_suggestions',
  number_last_played_to_exclude: 3,
  num_warfare_options: 4,
  num_offensive_options: 2,
  num_skirmish_control_options: 1,
  consider_offensive_same_map: true,
  consider_skirmishes_as_same_map: true,
  allow_consecutive_offensives: true,
  allow_consecutive_offensives_opposite_sides: false,
  allow_default_to_offensive: false,
  allow_consecutive_skirmishes: false,
  allow_default_to_skirmish: false,
  instruction_text:
    'Vote for the nextmap:\nType in the chat !votemap <map number>\n{map_selection}\n\nTo never see this message again type in the chat !votemap never\n\nTo renable type: !votemap allow',
  thank_you_text: 'Thanks {player_name}, vote registered for:\n{map_name}',
  no_vote_text: 'No votes recorded yet',
  reminder_frequency_minutes: 20,
  allow_opt_out: true,
  help_text: '',
};

export const VotemapConfigForm = () => {
  const [formChanged, setFormChanged] = React.useState(false);

  const { config: serverConfig } = useLoaderData();

  const submit = useSubmit();

  const actionData = useActionData();

  const [config, setConfig] = React.useState(serverConfig);

  React.useEffect(() => {
    if (actionData?.ok) {
      setFormChanged(false);
    }
  }, [actionData])

  const handleFactoryConfig = () => {
    setConfig(FACTORY_CONFIG);
  };

  const handleResetConfigChanges = () => {
    setConfig(serverConfig);
  };

  const handleInputChange = (e) => {
    let { name, value } = e.target;

    if (typeof config[name] === 'boolean') {
      setConfig(prevConfig => {
        if (prevConfig[name]) {
            value = false;
        } else {
            value = true;
        }

        return {
            ...prevConfig,
            [name]: value,
          }
      });
      return;
    }

    setConfig({
      ...config,
      [name]: value,
    });
  };

  const handleFormSubmit = (e) => {
    const formData = new FormData();
    Object.entries(config).forEach(entry => formData.append(...entry));
    formData.append('intent', 'set_config');
    submit(formData, { method: 'post' });
    e.preventDefault();
  }

  const totalMapOptions =
    Number(config.num_warfare_options) +
    Number(config.num_offensive_options) +
    Number(config.num_skirmish_control_options);

  return (
    <Form onSubmit={handleFormSubmit} onChange={() => setFormChanged(true)}>
      <Wrapper direction={'row'}>
        {/* Panel */}
        <FormCard fullWidth>
          <Stack
            direction="row"
            gap={1}
            alignItems={'center'}
            flexWrap={'wrap'}
          >
            <Typography variant="h6">Votemap Config</Typography>
            <Box sx={{ flexGrow: 1 }}></Box>
            <StyledFormControlLabel
              sx={{ marginLeft: 0, marginRight: 2 }}
              labelPlacement="start"
              control={
                <Switch
                  onChange={handleInputChange}
                  checked={config.enabled}
                  color="warning"
                  name="enabled"
                />
              }
              label={config.enabled ? "ON" : "OFF"}
            />
            <Button
              size="small"
              variant="contained"
              onClick={() => {
                setFormChanged(true);
                handleFactoryConfig();
              }}
              color="warning"
            >
              Factory Settings
            </Button>
            <Button
              size="small"
              variant="contained"
              onClick={() => {
                setFormChanged(false);
                handleResetConfigChanges();
              }}
              color="warning"
              disabled={!formChanged}
            >
              Reset Changes
            </Button>
            <Button
              size="small"
              name="intent"
              value="set_config"
              variant="contained"
              type="submit"
              disabled={!formChanged}
            >
              Save
            </Button>
          </Stack>
        </FormCard>
        {/* Generating Map Options (1/2) */}
        <FormCard>
          <FormCardTitle>Generating Map Options (1/2)</FormCardTitle>
          <Typography>Description</Typography>
          <FormDivider />
          <Typography sx={{ mb: 1 }}>
            Total map options: {totalMapOptions}
          </Typography>
          <TextField
            onChange={handleInputChange}
            name="num_warfare_options"
            label="Warfare maps"
            variant="outlined"
            value={config.num_warfare_options}
            margin="normal"
            fullWidth
            type="number"
            inputProps={{
              min: 0,
            }}
          />
          <TextField
            onChange={handleInputChange}
            name="num_offensive_options"
            label="Offensive maps"
            variant="outlined"
            value={config.num_offensive_options}
            margin="normal"
            fullWidth
            type="number"
            inputProps={{
              min: 0,
            }}
          />
          <TextField
            onChange={handleInputChange}
            name="num_skirmish_control_options"
            label="Skirmish maps"
            variant="outlined"
            value={config.num_skirmish_control_options}
            margin="normal"
            fullWidth
            type="number"
            inputProps={{
              min: 0,
            }}
          />
          <SwitchHelperText variant="caption">
            Number of maps in the vote selection
          </SwitchHelperText>
        </FormCard>
        {/* Generating Map Options (2/2) */}
        <FormCard>
          <FormCardTitle>Generating Map Options (2/2)</FormCardTitle>
          <Typography>Description</Typography>
          <FormDivider textAlign="left" flexItem>
            Skirmish
          </FormDivider>
          <FormGroup sx={{ alignItems: 'start' }}>
            <StyledFormControlLabel
              labelPlacement="end"
              control={
                <Switch
                  onChange={handleInputChange}
                  name="consider_offensive_same_map"
                  checked={config.consider_offensive_same_map}
                />
              }
              label="Exclude Skirmish"
            />
            <SwitchHelperText variant="caption">
              Consider a <strong>Skirmish</strong> map being the same as a
              warfare map, when excluding
            </SwitchHelperText>
            <StyledFormControlLabel
              labelPlacement="end"
              control={
                <Switch
                  onChange={handleInputChange}
                  name="allow_consecutive_skirmishes"
                  checked={config.allow_consecutive_skirmishes}
                />
              }
              label="Consecutive Skirmish"
            />
            <SwitchHelperText variant="caption">
              Allow consecutive <strong>Skirmish</strong> map
            </SwitchHelperText>
            <FormDivider textAlign="left" flexItem>
              Offensive
            </FormDivider>
            <StyledFormControlLabel
              labelPlacement="end"
              control={
                <Switch
                  onChange={handleInputChange}
                  name="consider_skirmishes_as_same_map"
                  checked={config.consider_skirmishes_as_same_map}
                />
              }
              label="Exclude Offensive"
            />
            <SwitchHelperText variant="caption">
              Consider an <strong>Offensive</strong> map being the same as a
              warfare map, when excluding
            </SwitchHelperText>
            <StyledFormControlLabel
              labelPlacement="end"
              control={
                <Switch
                  onChange={handleInputChange}
                  name="allow_consecutive_offensives"
                  checked={config.allow_consecutive_offensives}
                />
              }
              label="Consecutive Offensive"
            />
            <SwitchHelperText variant="caption">
              Allow consecutive <strong>Offensive</strong> map
            </SwitchHelperText>
            <StyledFormControlLabel
              labelPlacement="end"
              control={
                <Switch
                  onChange={handleInputChange}
                  name="allow_consecutive_offensives_opposite_sides"
                  checked={
                    config.allow_consecutive_offensives_opposite_sides
                  }
                />
              }
              label="Consecutive offensive, same side"
            />
            <SwitchHelperText variant="caption">
              Allow consecutive <strong>Offensive</strong> where a team would
              play defense/offense twice in a row, eg. off_ger followed by
              off_us
            </SwitchHelperText>
            <FormDivider />
            <TextField
              onChange={handleInputChange}
              name="number_last_played_to_exclude"
              label="Excluded last played maps"
              variant="outlined"
              value={config.number_last_played_to_exclude}
              margin="normal"
              fullWidth
              type="number"
              inputProps={{
                min: 0,
              }}
            />
          </FormGroup>
        </FormCard>
        {/* Default Map Pick */}
        <FormCard>
          <FormCardTitle>Default Map Pick</FormCardTitle>
          <Typography>Description</Typography>
          <FormDivider />
          <FormControl>
            <FormLabel id="default-map-pick-method">Method</FormLabel>
            <RadioGroup
              aria-labelledby="default-map-pick-method"
              value={config.default_method}
              name="default_method"
              onChange={handleInputChange}
            >
              <FormControlLabel
                value="least_played_from_suggestions"
                control={<Radio />}
                label="The least played from selection"
              />
              <FormControlLabel
                value="least_played_from_all_map"
                control={<Radio />}
                label="The least played from all"
              />
              <FormControlLabel
                value="random_from_suggestions"
                control={<Radio />}
                label="Random from selection"
              />
              <FormControlLabel
                value="random_from_all_maps"
                control={<Radio />}
                label="Random from all"
              />
            </RadioGroup>
          </FormControl>
          <FormDivider />
          <FormGroup sx={{ alignItems: 'start' }}>
            <StyledFormControlLabel
              labelPlacement="end"
              control={
                <Switch
                  name="allow_default_to_offensive"
                  checked={config.allow_default_to_offensive}
                  onChange={handleInputChange}
                />
              }
              label="Default Offensive"
            />
            <SwitchHelperText variant="caption">
              Allow <strong>Offensive</strong> as default map
            </SwitchHelperText>
            <StyledFormControlLabel
              labelPlacement="end"
              control={
                <Switch
                  name="allow_default_to_skirmish"
                  checked={config.allow_default_to_skirmish}
                  onChange={handleInputChange}
                />
              }
              label="Default Skirmish"
            />
            <SwitchHelperText variant="caption">
              Allow <strong>Skirmish</strong> as default map
            </SwitchHelperText>
          </FormGroup>
        </FormCard>
        {/* Reminder */}
        <FormCard>
          <FormCardTitle>Reminder</FormCardTitle>
          <Typography>
            A reminder message that will be sent to players who haven't voted
            yet. When frequency set to 0, this reminder will be shown only once
            on map end.
          </Typography>
          <FormDivider />
          <FormGroup sx={{ alignItems: 'start', mb: 1 }}>
            <StyledFormControlLabel
              labelPlacement="end"
              control={
                <Switch
                  name="allow_opt_out"
                  checked={config.allow_opt_out}
                  onChange={handleInputChange}
                />
              }
              label="Map Vote Opt Out"
            />
            <SwitchHelperText variant="caption">
              Allow users to opt out of map vote reminders by using the command
              `!votemap never`
            </SwitchHelperText>
          </FormGroup>
          <TextField
            onChange={handleInputChange}
            name="reminder_frequency_minutes"
            label="Reminder frequency during game"
            variant="outlined"
            value={config.reminder_frequency_minutes}
            margin="normal"
            fullWidth
            type="number"
            helperText="Set to 0 to disable."
            inputProps={{
              min: 0,
            }}
          />
          <TextField
            onChange={handleInputChange}
            name="instruction_text"
            multiline
            minRows={4}
            label="Message"
            variant="filled"
            value={config.instruction_text}
            helperText="Make sure you add {map_selection} in your text"
            margin="normal"
            fullWidth
            type="text"
          />
        </FormCard>
        {/* Messages */}
        <FormCard>
          <FormCardTitle>Messages</FormCardTitle>
          <TextField
            onChange={handleInputChange}
            name="thank_you_text"
            multiline
            minRows={4}
            label="Vote Response"
            variant="filled"
            value={config.thank_you_text}
            helperText="The reply to player after they voted. You can use {player_name} and {map_name} in the text. Leave blank if you don't want the confirmation message"
            margin="normal"
            fullWidth
            type="text"
          />
          <TextField
            onChange={handleInputChange}
            name="help_text"
            multiline
            minRows={4}
            label="Vote Help"
            variant="filled"
            value={config.help_text}
            helperText="Help text:
          This text will show to the player in case of a bad !votemap command, or if the user types !votemap help"
            margin="normal"
            fullWidth
            type="text"
          />
          <TextField
            onChange={handleInputChange}
            name="no_vote_text"
            multiline
            minRows={4}
            label="No Vote Text"
            variant="filled"
            value={config.no_vote_text}
            helperText="This text will be shown as Broadcast message when no map has been voted."
            margin="normal"
            fullWidth
            type="text"
          />
        </FormCard>
      </Wrapper>
    </Form>
  );
};
