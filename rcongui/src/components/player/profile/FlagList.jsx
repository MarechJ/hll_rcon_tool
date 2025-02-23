import { Stack, Typography } from "@mui/material";
import Emoji from "@/components/shared/Emoji";

const FlagList = ({ flags }) => {
  if (!flags.length) {
    return <Typography>No flags found</Typography>;
  }
  
    return (
      <Stack>
        {flags.map(({ flag, comment, modified }) => (
          <Stack direction="row" alignItems="center" spacing={1} key={flag}>
            <Typography>
              <Emoji emoji={flag} />
            </Typography>
            <Typography variant="body2">{comment || "[no comment]"}</Typography>
          </Stack>
        ))}
      </Stack>
  );
};

export default FlagList;
