import { Link, Skeleton, Typography } from '@mui/material';
import Grid from '@mui/material/Grid2';
import {
  get as apiGet,
  handle_http_errors,
  showResponse,
} from '@/utils/fetchUtils';
import {useEffect, useState} from "react";

const Footer = () => {
  const [loading, setLoading] = useState(true);
  const [repoData, setRepoData] = useState([]);
  const [apiVersion, setApiVersion] = useState('N/A');

  useEffect(() => {
    async function onLoad() {
      setLoading(true);
      try {
        const gitResponse = await fetch(
          'https://api.github.com/repos/MarechJ/hll_rcon_tool/contributors'
        );

        if (gitResponse.status !== 200) {
          throw new Error('Rate limited');
        }

        setRepoData(await gitResponse.json());
      } catch (error) {
        console.error('Something went wrong parsing github data.');
      }

      try {
        const apiResponse = await apiGet('get_version');
        const apiData = await showResponse(apiResponse, 'get_version', false);
        setApiVersion(apiData.result);
      } catch (error) {
        handle_http_errors(error);
      }
      setLoading(false);
    }

    onLoad();
  }, []);

  const contributors = repoData
    .filter((d) => d.type === 'User')
    .map((d) => (
      <Link key={d.login} target="_blank" href={d.html_url}>
        {`${d.login} (${d.contributions})`},{' '}
      </Link>
    ));

  const appInfo = `UI Version: ${process.env.REACT_APP_VERSION} API Version: ${apiVersion} - Brought to you by Dr.WeeD, `;

  return loading ? (
    <Skeleton height={'10rem'} width={'100%'} />
  ) : (
    <Grid container component={'footer'} sx={{ minHeight: '10rem' }}>
      <Grid size={12}>
        <Typography
          color="textSecondary"
          variant="caption"
          display="block"
          gutterBottom
        >
          {appInfo}
          {contributors}
        </Typography>
      </Grid>
      {!process.env.REACT_APP_PUBLIC_BUILD ? (
        <Grid size={12}>
          <Typography
            color="textSecondary"
            variant="caption"
            display="block"
            gutterBottom
          >
            Join{' '}
            <Link target="_blank" href="https://discord.gg/zpSQQef">
              the discord
            </Link>{' '}
            for announcements, questions, feedback and support. Dev or docs
            contributions are most welcomed.
          </Typography>
        </Grid>
      ) : null}
    </Grid>
  );
};

export default Footer;
