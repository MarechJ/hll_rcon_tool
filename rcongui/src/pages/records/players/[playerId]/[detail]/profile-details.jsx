import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Divider,
  IconButton,
  List,
  ListItem,
  Stack,
  Grid2 as Grid,
} from "@mui/material";
import { useOutletContext } from "react-router-dom";
import EditIcon from "@mui/icons-material/Edit";
import { useEditSoldierModal } from "@/hooks/useEditSoldierModal";
import MilitaryTechIcon from "@mui/icons-material/MilitaryTech";
import CopyableText from "@/components/shared/CopyableText";
import { useEditAccountModal } from "@/hooks/useEditAccountModal";
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import { CountryFlag } from "@/components/shared/CountryFlag";
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import PlatformChip from "@/components/player/profile/Platform";
import LevelChip from "@/components/player/profile/Level";

const ProfileDetails = () => {
  const { profile } = useOutletContext();

  return (
    <Grid container spacing={2}>
      <Grid size={{ xs: 12, md: 6 }}>
        <SoldierCard profile={profile} />
      </Grid>
      <Grid size={{ xs: 12, md: 6 }}>
        <AccountCard profile={profile} />
      </Grid>
    </Grid>
  );
};

const SoldierCard = ({ profile }) => {
  const { soldier } = profile;
  const { openModal: editSoldier, modal: soldierEditForm } =
    useEditSoldierModal(profile.player_id, soldier);

  return (
    <>
      <Card>
        <CardHeader
          title={
            <Stack direction={"row"} gap={1} alignItems={"center"} fontSize={"1rem"}>
              <MilitaryTechIcon sx={{ width: "1rem", height: "1rem" }} />
              Soldier
            </Stack>
          }
          subheader={"Persistent in-game info updated upon each connection"}
          action={
            <IconButton
              aria-label="edit soldier"
              onClick={editSoldier}
              size={"small"}
            >
              <EditIcon sx={{ width: "1rem", height: "1rem" }} />
            </IconButton>
          }
        />
        <CardContent sx={{ display: "flex" }}>
          <List sx={{ flexGrow: 1, "& > *": {} }}>
            <ListItem sx={{ display: "flex", justifyContent: "space-between" }}>
              <Box sx={{ color: (theme) => theme.palette.text.secondary }}>
                Name:
              </Box>
              <Box>
                <CopyableText
                  text={soldier["name"]}
                  label={soldier["name"]}
                  position="start"
                />
              </Box>
            </ListItem>
            <ListItem sx={{ display: "flex", justifyContent: "space-between" }}>
              <Box sx={{ color: (theme) => theme.palette.text.secondary }}>
                Clan Tag:
              </Box>
              <Box>{soldier["clan_tag"]}</Box>
            </ListItem>
            <ListItem sx={{ display: "flex", justifyContent: "space-between" }}>
              <Box sx={{ color: (theme) => theme.palette.text.secondary }}>
                Level:
              </Box>
              <Box><LevelChip level={soldier["level"]} /></Box>
            </ListItem>
            <ListItem sx={{ display: "flex", justifyContent: "space-between" }}>
              <Box sx={{ color: (theme) => theme.palette.text.secondary }}>
                Platform:
              </Box>
              <Box><PlatformChip platform={soldier["platform"]} playerId={profile.player_id} /></Box>
            </ListItem>
            <ListItem sx={{ display: "flex", justifyContent: "space-between" }}>
              <Box sx={{ color: (theme) => theme.palette.text.secondary }}>
                EOS ID:
              </Box>
              <Box>
                <CopyableText
                  text={soldier["eos_id"]}
                  label={soldier["eos_id"]}
                  position="start"
                />
              </Box>
            </ListItem>
          </List>
        </CardContent>
      </Card>
      {soldierEditForm}
    </>
  );
};

const AccountCard = ({ profile }) => {
  const { account } = profile;
  const { openModal: editSoldier, modal: accountEditForm } =
    useEditAccountModal(profile.player_id, account);

  return (
    <>
      <Card>
        <CardHeader
          title={
            <Stack direction={"row"} gap={1} alignItems={"center"} fontSize={"1rem"}>
              <AccountCircleIcon sx={{ width: "1rem", height: "1rem" }} />
              Account
            </Stack>
          }
          subheader={"CRCON DB info linked to this player(soldier)"}
          action={
            <IconButton
              aria-label="edit account"
              onClick={editSoldier}
              size={"small"}
            >
              <EditIcon sx={{ width: "1rem", height: "1rem" }} />
            </IconButton>
          }
        />
        <CardContent sx={{ display: "flex" }}>
          <List sx={{ flexGrow: 1 }}>
            <ListItem sx={{ display: "flex", justifyContent: "space-between" }}>
              <Box sx={{ color: (theme) => theme.palette.text.secondary }}>
                Name:
              </Box>
              <Box>
                {account["name"] ? (<CopyableText
                  text={account["name"]}
                  label={account["name"]}
                  position="start"
                />) : "-"}
              </Box>
            </ListItem>
            <ListItem sx={{ display: "flex", justifyContent: "space-between" }}>
              <Box sx={{ color: (theme) => theme.palette.text.secondary }}>
                Country:
              </Box>
              <Box>{account["country"]
                ? <><CountryFlag country={account["country"]} /> {account["country"]}</>
                : "-"
              }</Box>
            </ListItem>
            <ListItem sx={{ display: "flex", justifyContent: "space-between" }}>
              <Box sx={{ color: (theme) => theme.palette.text.secondary }}>
                Lang:
              </Box>
              <Box>{account["lang"]}</Box>
            </ListItem>
            <ListItem sx={{ display: "flex", justifyContent: "space-between" }}>
              <Box sx={{ color: (theme) => theme.palette.text.secondary }}>
                Discord ID:
              </Box>
              <Box>
                {account["discord_id"] ? (<CopyableText
                  text={account["discord_id"]}
                  label={account["discord_id"]}
                  position="start"
                />) : "-"}
              </Box>
            </ListItem>
            <ListItem sx={{ display: "flex", justifyContent: "space-between" }}>
              <Box sx={{ color: (theme) => theme.palette.text.secondary }}>
                Membership:
              </Box>
              <Box>{account["is_member"] ? <CheckCircleIcon style={{color: "green"}} /> : <CancelIcon style={{color: "red"}} />}</Box>
            </ListItem>
          </List>
        </CardContent>
      </Card>
      {accountEditForm}
    </>
  );
};

export default ProfileDetails;
