import React from "react";
import { Grid, Typography, Link } from "@material-ui/core";
import { join } from "lodash/array";

const Footer = () => {
  const [repoData, setRepoData] = React.useState([]);
  React.useEffect(
    () =>
      fetch("https://api.github.com/repos/MarechJ/hll_rcon_tool/contributors")
        .then((response) => response.json())
        .then((data) => setRepoData(data)),
    []
  );

  return (
    <Grid container>
      <Grid xs={12}>
        <Typography
          color="textSecondary"
          variant="caption"
          display="block"
          gutterBottom
        >
          Brought to you by Dr.WeeD,{" "}
          {repoData
            .filter((d) => d.type === "User")
            .map((d) => (
              <Link target="_blank" href={d.html_url}>
                {`${d.login} (${d.contributions})`},{" "}
              </Link>
            ))}
        </Typography>
      </Grid>
      <Grid xs={12}>
        <Typography
          color="textSecondary"
          variant="caption"
          display="block"
          gutterBottom
        >
          Join{" "}
          <Link target="_blank" href="https://discord.gg/zpSQQef">
            the discord
          </Link>{" "}
          for announcements, questions, feedback and support. Dev or docs contributions are
          most welcomed.
        </Typography>
      </Grid>
    </Grid>
  );
};

export default Footer;
