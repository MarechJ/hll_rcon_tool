import React from 'react';
import { Box, Button, Stack, Switch } from '@mui/material';
import {
  FormCard,
  FormCardContent,
  FormCardHeader,
  FormCardTitle,
  FormDescription,
  StyledFormControlLabel,
  Wrapper,
} from './cards';
import { Form } from 'react-router-dom';
import SliderWithInputField from '../form/core/SliderWithInputField';
import BalanceIcon from '@mui/icons-material/Balance';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import SnoozeIcon from '@mui/icons-material/Snooze';
import NetworkCheckIcon from '@mui/icons-material/NetworkCheck';
import QueueIcon from '@mui/icons-material/Queue';
import WorkspacePremiumIcon from '@mui/icons-material/WorkspacePremium';

export const Basic = ({ settings: originalSettings }) => {
  const [settings, setSettings] = React.useState(originalSettings);

  const resetChanges = () => {
    setSettings(originalSettings);
  };

  const toggleSettings = (name) => (event) => {

  }

  const handleInputChange = (e) => {
    let { name, value } = e.target;

    if (typeof settings[name] === 'boolean') {
      setConfig((prevSettings) => {
        if (prevSettings[name]) {
          value = false;
        } else {
          value = true;
        }

        return {
          ...prevSettings,
          [name]: value,
        };
      });
      return;
    }

    setSettings({
      ...settings,
      [name]: value,
    });
  };

  // Hook all fields to `settings` values

  return (
    <Wrapper direction={'row'} sx={{ px: 1 }}>
      {/* Panel */}
      <FormCard fullWidth sx={{ mr: 1 }}>
        <Stack direction="row" gap={1} alignItems={'center'} flexWrap={'wrap'}>
          <FormCardTitle>Basic Server Settings</FormCardTitle>
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
            value="set_serversettings"
            variant="contained"
            type="submit"
            size="small"
          >
            Save
          </Button>
        </Stack>
      </FormCard>
      {/* Team Switch Cooldown */}
      <FormCard>
        <FormCardHeader
          sx={{
            display: 'flex',
            flexDirection: 'row',
            justifyContent: 'space-between',
          }}
        >
          <FormCardTitle>Team Switch Cooldown</FormCardTitle>
          <StyledFormControlLabel
            labelPlacement="start"
            control={<Switch checked={false} name="enabled" />}
          />
        </FormCardHeader>
        <FormCardContent>
          <SliderWithInputField
            icon={<SwapHorizIcon />}
            min={0}
            max={30}
            step={1}
            value={settings.team_switch_cooldown}
            label={'Cooldown (min)'}
            name={'team_switch_cooldown'}
            disabled={false}
            onChange={handleInputChange}
          />
        </FormCardContent>
        <FormDescription descFor={'Team Switch Cooldown'}>
          This setting allows you to control the cooldown period for team
          switching. When set to 0, team switching is disabled. Otherwise, you
          can specify a positive value in minutes to determine how long players
          must wait before switching teams again.
        </FormDescription>
      </FormCard>
      {/* Team Count Balance */}
      <FormCard>
        <FormCardHeader
          sx={{
            display: 'flex',
            flexDirection: 'row',
            justifyContent: 'space-between',
          }}
        >
          <FormCardTitle>Team Count Balance</FormCardTitle>
          <StyledFormControlLabel
            labelPlacement="start"
            control={<Switch checked={false} name="enabled" />}
          />
        </FormCardHeader>
        <FormCardContent>
          <SliderWithInputField
            icon={<BalanceIcon />}
            min={0}
            max={50}
            step={1}
            value={settings.autobalance_threshold}
            label={'Threshold'}
            name={'autobalance_threshold'}
            disabled={false}
          />
        </FormCardContent>
        <FormDescription descFor={'Team Count Balance'}>
          This setting allows you to manage the difference in player count
          between teams. When enabled, players will be restricted from joining a
          team if it would create an imbalance beyond a specified threshold. If
          disabled, players can freely join any team regardless of the
          difference in player count.
        </FormDescription>
      </FormCard>
      {/* Idle Kick */}
      <FormCard>
        <FormCardHeader
          sx={{
            display: 'flex',
            flexDirection: 'row',
            justifyContent: 'space-between',
          }}
        >
          <FormCardTitle>Idle Kick</FormCardTitle>
          <StyledFormControlLabel
            labelPlacement="start"
            control={<Switch checked={false} name="enabled" />}
          />
        </FormCardHeader>
        <FormCardContent>
          <SliderWithInputField
            icon={<SnoozeIcon />}
            min={0}
            max={200}
            step={5}
            value={0}
            defaultValue={5}
            label={'Time (min)'}
            name={'TODO'}
            disabled={false}
          />
        </FormCardContent>
        <FormDescription descFor={'Idle Kick'}>
          This setting allows you to control how long a player can remain idle
          before being automatically kicked from the game. When set to 0, idle
          autokick is disabled. Otherwise, you can specify a positive value in
          minutes to determine the idle threshold.
        </FormDescription>
      </FormCard>
      {/* Max Ping */}
      <FormCard>
        <FormCardHeader
          sx={{
            display: 'flex',
            flexDirection: 'row',
            justifyContent: 'space-between',
          }}
        >
          <FormCardTitle>Max Ping</FormCardTitle>
          <StyledFormControlLabel
            labelPlacement="start"
            control={<Switch checked={false} name="enabled" />}
          />
        </FormCardHeader>
        <FormCardContent>
          <SliderWithInputField
            icon={<NetworkCheckIcon />}
            min={0}
            max={2000}
            step={10}
            value={0}
            defaultValue={500}
            label={'Ping (ms)'}
            name={'TODO'}
            disabled={false}
          />
        </FormCardContent>
        <FormDescription descFor={'Max Ping'}>
          This setting allows you to control the maximum acceptable ping
          (latency) for players in the game. When set to 0, the maximum ping
          check is disabled. Otherwise, you can specify a positive value in
          milliseconds to limit the allowable ping for players.
        </FormDescription>
      </FormCard>
      {/* Max Queue Length */}
      <FormCard>
        <FormCardHeader
          sx={{
            display: 'flex',
            flexDirection: 'row',
            justifyContent: 'space-between',
          }}
        >
          <FormCardTitle>Max Queue Length</FormCardTitle>
          <StyledFormControlLabel
            labelPlacement="start"
            control={<Switch checked={false} name="enabled" />}
          />
        </FormCardHeader>
        <FormCardContent>
          <SliderWithInputField
            icon={<QueueIcon />}
            min={0}
            max={6}
            step={1}
            value={0}
            defaultValue={6}
            label={'Length'}
            name={'TODO'}
            disabled={false}
          />
        </FormCardContent>
        <FormDescription descFor={'Max Queue Length'}>
          This setting determines the maximum number of people allowed to wait
          in a queue. When the queue reaches this limit, additional players will
          be prevented from joining until there is space available.
        </FormDescription>
      </FormCard>
      {/* VIP Slots */}
      <FormCard>
        <FormCardHeader
          sx={{
            display: 'flex',
            flexDirection: 'row',
            justifyContent: 'space-between',
          }}
        >
          <FormCardTitle>VIP Slots</FormCardTitle>
          <StyledFormControlLabel
            labelPlacement="start"
            control={<Switch checked={false} name="enabled" />}
          />
        </FormCardHeader>
        <FormCardContent>
          <SliderWithInputField
            icon={<WorkspacePremiumIcon />}
            min={0}
            max={100}
            step={1}
            value={0}
            defaultValue={1}
            label={'Slots'}
            name={'TODO'}
            disabled={false}
          />
        </FormCardContent>
        <FormDescription descFor={'VIP Slots'}>
          This setting allows you to designate a certain number of slots
          exclusively for VIP players. When VIP slots are enabled, only players
          with VIP status can occupy these reserved slots. Other players will be
          unable to join the game through these slots.
        </FormDescription>
      </FormCard>
    </Wrapper>
  );
};
