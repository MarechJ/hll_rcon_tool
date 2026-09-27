import { Icon, Stack, Tooltip } from "@mui/material";
import Emoji from "@/components/shared/Emoji";
import { ActionIconButton } from "@/features/player-action/ActionMenu";
import { Actions } from "@/features/player-action/actions";

const FlagList = ({ player }) => {
  return (
    <Stack direction="row" alignItems="center" spacing={0.5}>
      <ActionIconButton
        action={Actions.AddFlag}
        recipients={[player]}
        sx={{ fontSize: "1em", opacity: 0.35 }}
      />
      {player?.flags?.map(({ flag, comment, managed_by_vip_list }) => (
        <Stack direction="row" alignItems="center" spacing={1} key={flag}>
          {managed_by_vip_list ? (
            <Tooltip title="Managed by VIP Lists · Change this in the list settings">
              <Icon sx={{ fontSize: "1em" }}>
                <Emoji emoji={flag} />
              </Icon>
            </Tooltip>
          ) : (
            <ActionIconButton
              action={Actions.RemoveFlag}
              recipients={[player]}
              params={{ flag }}
              icon={
                <Icon sx={{ fontSize: "1em" }}>
                  <Emoji emoji={flag} />
                </Icon>
              }
              label={comment}
            />
          )}
        </Stack>
      ))}
    </Stack>
  );
};

export default FlagList;
