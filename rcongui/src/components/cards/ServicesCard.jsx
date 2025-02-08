import { useQuery } from "@tanstack/react-query";
import { cmd } from "@/utils/fetchUtils";
import {
  Card,
  CardHeader,
  CardContent,
  IconButton,
  Typography,
  Box,
  Grid2 as Grid,
  Stack,
  Tooltip,
} from "@mui/material";
import { Link } from "react-router-dom";
import { useMemo } from "react";
import SettingsIcon from '@mui/icons-material/Settings';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import ErrorIcon from '@mui/icons-material/Error';
import BlockIcon from '@mui/icons-material/Block';
import InfoIcon from '@mui/icons-material/Info';

const ServicesCard = () => {
  const { data: services = [] } = useQuery({
    queryKey: ["settings", "services"],
    queryFn: async () => {
      const result = await cmd.GET_SERVICES();
      return result;
    },
  });

  // Group services by their state
  const groupedServices = useMemo(() => {
    const groups = {
      RUNNING: [],
      STOPPED: [],
      FATAL: [],
      EXITED: []
    };

    services.forEach(service => {
      const state = service.statename;
      if (groups[state] !== undefined) {
        groups[state].push(service);
      }
    });

    return groups;
  }, [services]);

  // Helper function to get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'RUNNING':
        return 'success.main';
      case 'STOPPED':
        return 'warning.main';
      case 'FATAL':
        return 'error.main';
      case 'EXITED':
        return 'text.disabled';
      default:
        return 'text.secondary';
    }
  };

  // Helper function to get status icon
  const StatusIcon = ({ status }) => {
    switch (status) {
      case 'RUNNING':
        return <PlayArrowIcon sx={{ fontSize: '1.2rem', color: getStatusColor(status) }} />;
      case 'STOPPED':
        return <StopIcon sx={{ fontSize: '1.2rem', color: getStatusColor(status) }} />;
      case 'FATAL':
        return <ErrorIcon sx={{ fontSize: '1.2rem', color: getStatusColor(status) }} />;
      case 'EXITED':
        return <BlockIcon sx={{ fontSize: '1.2rem', color: getStatusColor(status) }} />;
      default:
        return null;
    }
  };

  const ServiceItem = ({ service }) => (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1,
        py: 0.5,
      }}
    >
      <StatusIcon status={service.statename} />
      <Box sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <Typography variant="body2" sx={{ fontWeight: 500 }}>
            {service.name}
          </Typography>
          {service.info && (
            <Tooltip title={service.info}>
              <InfoIcon sx={{ fontSize: '1rem', color: 'text.secondary' }} />
            </Tooltip>
          )}
        </Box>
      </Box>
    </Box>
  );

  const ServiceGroup = ({ status, services }) => (
    <Box>
      <Typography 
        variant="subtitle2" 
        color="text.secondary" 
        sx={{ 
          mb: 1,
          display: 'flex',
          alignItems: 'center',
          gap: 0.5 
        }}
      >
        <StatusIcon status={status} />
        {status} ({services.length})
      </Typography>
      <Stack spacing={1}>
        {services.map(service => (
          <ServiceItem key={service.name} service={service} />
        ))}
      </Stack>
    </Box>
  );

  return (
    <Card sx={{ height: '100%' }}>
      <CardHeader 
        title="Services" 
        action={
          <IconButton 
            component={Link} 
            to="/settings/services"
            size="small"
            sx={{ color: 'text.secondary' }}
          >
            <SettingsIcon />
          </IconButton>
        }
      />
      <CardContent>
        <Grid container spacing={2}>
          {Object.entries(groupedServices).map(([status, servicesList]) => (
            <Grid key={status} size={{ xs: 12, md: 3 }}>
              <ServiceGroup status={status} services={servicesList} />
            </Grid>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );
};

export default ServicesCard; 