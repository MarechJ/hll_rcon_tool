import { ActionMenuButton } from "@/features/player-action/ActionMenu";
import React from "react";

function ProfileActions({ player, actions, sx, ...props }) {
  return (
    <ActionMenuButton
      recipients={player}
      actions={actions}
      size="small"
      sx={{ width: 24, height: 24, ...sx }}
      withProfile
      {...props}
    />
  );
}

export default ProfileActions;
