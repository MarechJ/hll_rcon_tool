import Padlock from "@/components/shared/Padlock";
import SplitButton from "@/components/shared/SplitButton";
import { cmd } from "@/utils/fetchUtils";
import { Box, Paper, Slider, Stack, TextField, Typography, Grid2 as Grid, Input, Button } from "@mui/material";
import { useMemo, useState } from 'react';
import { useLoaderData } from "react-router-dom";

/*
Settings object
{
    "team_switch_cooldown": 5,
    "autobalance_threshold": 1,
    "idle_autokick_time": 0,
    "max_ping_autokick": 0,
    "queue_length": 6,
    "vip_slots_num": 2,
    "autobalance_enabled": true,
    "votekick_enabled": true,
    "votekick_thresholds": "[(0, 1), (10, 5), (25, 12), (50, 20)]"
}
*/

const INTENT = {
    SINGLE: 0,
    ALL: 1,
};

const VOTEKICK_THRESHOLDS = [
    [0, 1],
];

export const loader = async () => {
    const settings = await cmd.GET_SERVER_SETTINGS();
    return { settings };
};

export const action = async ({ request }) => {
    const { settings, ...rest } = Object.fromEntries(await request.formData());
    const payload = { settings: settings.length ? settings.split(",") : [], ...rest };
    const result = await cmd.SET_SERVER_SETTINGS({ payload });
    return result;
};

const SettingsPage = () => {
    const { settings } = useLoaderData();
    const [localSettings, setLocalSettings] = useState(settings);

    console.log(parseVotekickThresholds(settings.votekick_thresholds));

    const submitChanges = (intent) => () => {
        console.log(intent);
    };

    const handleSliderChange = (key) => (event, newValue) => {
        setLocalSettings(prev => ({ ...prev, [key]: newValue }));
    };

    const handleInputChange = (key) => (event) => {
        const value = event.target.value === '' ? '' : Number(event.target.value);
        setLocalSettings(prev => ({ ...prev, [key]: value }));
    };

    const handleToggleChange = (key) => (checked) => {
        setLocalSettings(prev => ({ ...prev, [key]: checked }));
    };

    const handleBlur = (key) => () => {
        if (localSettings[key] < 0) {
            setLocalSettings(prev => ({ ...prev, [key]: 0 }));
        } else if (localSettings[key] > getMaxValue(key)) {
            setLocalSettings(prev => ({ ...prev, [key]: getMaxValue(key) }));
        }
    };

    const handleReset = () => {
        setLocalSettings(settings);
    };

    const settingsHasChanged = useMemo(() => {
        for (const key in settings) {
            if (settings[key] !== localSettings[key]) {
                return true;
            }
        }
        return false;
    }, [settings, localSettings]);

    return (
        <Box
            sx={{
                maxWidth: (theme) => theme.breakpoints.values.md,
            }}
        >
            <Stack
                component={Paper}
                direction={"row"}
                sx={{ p: 1, mb: 1 }}
                justifyContent={"end"}
                alignItems={"center"}
                gap={1}
            >
                <Button disabled={!settingsHasChanged} variant="contained" onClick={handleReset}>Reset</Button>
                <SplitButton
                    disabled={!settingsHasChanged}
                    options={[
                        {
                            name: "Apply",
                            buttonProps: {
                                onClick: submitChanges(INTENT.SINGLE),
                                disabled: !settingsHasChanged,
                            },
                        },
                        {
                            name: "Apply all servers",
                            buttonProps: {
                                onClick: submitChanges(INTENT.ALL),
                                disabled: !settingsHasChanged,
                            },
                        },
                    ]}
                />
            </Stack>
            <Stack spacing={4}>
                {Object.entries(localSettings)
                    .filter(([key]) => !['autobalance_enabled', 'votekick_enabled', 'votekick_thresholds'].includes(key))
                    .map(([key, value]) => (
                    <Box key={key} sx={{ width: '100%' }}>
                        <Typography variant="h6" id={`${key}-slider`} gutterBottom>
                            {/* Capitalize the first letter of each word */}
                            {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </Typography>
                        <Grid container spacing={4} sx={{ alignItems: 'center' }}>
                            <Grid size={{ xs: 10 }}>
                                <Slider
                                    value={typeof value === 'number' ? value : 0}
                                    onChange={handleSliderChange(key)}
                                    aria-labelledby={`${key}-slider`}
                                    max={getMaxValue(key)}
                                    marks={getMarks(key)}
                                    step={getStep(key)}
                                    valueLabelDisplay="auto"
                                    fullWidth
                                />
                            </Grid>
                            <Grid size={{ xs: 2 }}>
                                <Input
                                    value={value}
                                    size="small"
                                    onChange={handleInputChange(key)}
                                    onBlur={handleBlur(key)}
                                    inputProps={{
                                        step: getStep(key),
                                        min: 0,
                                        max: getMaxValue(key),
                                        type: 'number',
                                        'aria-labelledby': `${key}-slider`,
                                    }}
                                />
                            </Grid>
                        </Grid>
                        <Typography variant="caption" color="text.secondary">
                            {getHelpText(key)}
                        </Typography>
                    </Box>
                ))}
                <Box>
                    <Typography variant="h6" id="autobalance-slider" gutterBottom>
                        Autobalance {localSettings.autobalance_enabled ? "Enabled" : "Disabled"}
                    </Typography>
                    <Grid container spacing={4} sx={{ alignItems: 'center' }}>
                        <Grid size={{ xs: 10 }}>
                            <Padlock label="Autobalance" checked={localSettings.autobalance_enabled} handleChange={handleToggleChange('autobalance_enabled')} />
                        </Grid>
                    </Grid>
                    <Typography variant="caption" color="text.secondary">
                        Autobalance will automatically move players around to balance the teams.
                    </Typography>
                </Box>
                <Box>
                    <Typography variant="h6" id="votekick-slider" gutterBottom>
                        Votekick {localSettings.votekick_enabled ? "Enabled" : "Disabled"}
                    </Typography>
                    <Grid container spacing={4} sx={{ alignItems: 'center' }}>
                        <Grid size={{ xs: 10 }}>
                            <Padlock label="Votekick" checked={localSettings.votekick_enabled} handleChange={handleToggleChange('votekick_enabled')} />
                        </Grid>
                    </Grid>
                    <Typography variant="caption" color="text.secondary">
                        Votekick will allow players to votekick players from the server.
                    </Typography>
                </Box>
            </Stack>
        </Box>
    )
}

// Helper functions
const getMaxValue = (key) => {
    switch (key) {
        case 'team_switch_cooldown':
            return 30;
        case 'idle_autokick_time':
            return 200;
        case 'max_ping_autokick':
            return 2000;
        case 'queue_length':
            return 6;
        case 'vip_slots_num':
            return 100;
        default:
            return 100; // Default max value
    }
};

const getMarks = (key) => {
    switch (key) {
        case 'team_switch_cooldown':
            return [0, 5, 10, 15, 20, 25, 30].map(val => ({ value: val, label: `${val}` }));
        case 'idle_autokick_time':
            return [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200].map(val => ({ value: val, label: `${val}` }));
        case 'max_ping_autokick':
            return [0, 500, 1000, 1500, 2000].map(val => ({ value: val, label: `${val}` }));
        case 'queue_length':
            return [0, 1, 2, 3, 4, 5, 6].map(val => ({ value: val, label: `${val}` }));
        case 'vip_slots_num':
            return [0, 20, 40, 60, 80, 100].map(val => ({ value: val, label: `${val}` }));
        default:
            return [];
    }
};

const getHelpText = (key) => {
    switch (key) {
        case 'autobalance_threshold':
            return "0 means the teams must match exactly";
        case 'max_queue_length':
            return "Maximum # of people waiting";
        case 'vip_slots_num':
            return "# slots reserved for VIPs";
        default:
            return "0 to disable";
    }
};

const getStep = (key) => {
    switch (key) {
        case 'team_switch_cooldown':
            return 1;
        case 'idle_autokick_time':
        case 'max_ping_autokick':
            return 10;
        case 'queue_length':
        case 'vip_slots_num':
            return 1;
        default:
            return 1;
    }
};

const parseVotekickThresholds = (thresholds) => {
    // TODO: regex that captures the numbers found within the round brackets, eg [(0, 1), (10, 5), (25, 12), (50, 20)]
    const regex = /(\(\d+, \d+\))/g;
    const matches = thresholds.match(regex);
    const result = matches.map(match => match.slice(1, -1).split(", ").map(Number));
    return result;
};

export default SettingsPage;
