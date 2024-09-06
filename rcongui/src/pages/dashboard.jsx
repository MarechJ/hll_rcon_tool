import { Info, MoreVert } from '@mui/icons-material';
import {
  Avatar,
  Card,
  CardContent,
  CardHeader,
  IconButton,
  Typography,
} from '@mui/material';
import Grid from "@mui/material/Grid2"

const Dashboard = () => {
  return (
    (<Grid container columnSpacing={2} rowSpacing={2}>
      <Grid
        size={{
          xs: 12,
          md: 6
        }}>
        <Card sx={{ minHeight: '10rem', width: '100%' }}>
          <CardHeader
            title={'Title name'}
            subheader={'Description'}
            action={
              <IconButton>
                <MoreVert />
              </IconButton>
            }
            avatar={
              <Avatar>
                <Info />
              </Avatar>
            }
          />
          <CardContent>
            <Typography>Some content</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid
        size={{
          xs: 12,
          md: 6
        }}>
        <Card sx={{ minHeight: '10rem' }}>
          <CardHeader
            title={'Title name'}
            subheader={'Description'}
            action={
              <IconButton>
                <MoreVert />
              </IconButton>
            }
            avatar={
              <Avatar>
                <Info />
              </Avatar>
            }
          />
          <CardContent>
            <Typography>Some content</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid
        size={{
          xs: 12,
          md: 6
        }}>
        <Card sx={{ minHeight: '10rem' }}>
          <CardHeader
            title={'Title name'}
            subheader={'Description'}
            action={
              <IconButton>
                <MoreVert />
              </IconButton>
            }
            avatar={
              <Avatar>
                <Info />
              </Avatar>
            }
          />
          <CardContent>
            <Typography>Some content</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid
        size={{
          xs: 12,
          md: 6
        }}>
        <Card sx={{ minHeight: '10rem' }}>
          <CardHeader
            title={'Title name'}
            subheader={'Description'}
            action={
              <IconButton>
                <MoreVert />
              </IconButton>
            }
            avatar={
              <Avatar>
                <Info />
              </Avatar>
            }
          />
          <CardContent>
            <Typography>Some content</Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>)
  );
};

export default Dashboard;