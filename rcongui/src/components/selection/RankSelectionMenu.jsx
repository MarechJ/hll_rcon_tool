import { List, ListItem, ListItemButton, Box } from "@mui/material";
import { PopoverMenu } from "@/components/shared/PopoverMenu";
import { Tooltip, Button } from "@mui/material";
import MilitaryTechIcon from '@mui/icons-material/MilitaryTech';
import { sortByRank } from "@/utils/lib";
import { RankIcon } from "../shared/RankIcon";

/**
 * @typedef {Object} RankOption
 * @property {string} rank
 * @property {number} [count]
 */

/**
 * @param {Object} props
 * @param {Array<RankOption>} props.rankOptions
 * @param {Function} props.onRankSelect
 * @returns {JSX.Element}
 */
export const RankSelectionMenu = ({ rankOptions, onRankSelect }) => (
  <PopoverMenu
    id="rank-picker"
    description="Pick a rank to select all players with it"
    renderButton={(props) => (
      <Button {...props}>
        <Tooltip title="Select by rank">
          <MilitaryTechIcon />
        </Tooltip>
      </Button>
    )}
  >
    <List
      sx={{
        width: "100%",
        bgcolor: "background.paper",
        position: "relative",
        overflowY: "auto",
        overflowX: "hidden",
        maxHeight: 300,
        "& ul": { padding: 0 },
      }}
    >
      {[...rankOptions].sort((a, b) => sortByRank(a.rank, b.rank)).map((option, ) => (
        <ListItem
          key={option.rank}
          dense
          disableGutters
          sx={{ "& .MuiButtonBase-root": { opacity: 1 } }}
        >
          <ListItemButton onClick={() => onRankSelect(option)}>
            <Box sx={{ display: "flex", alignItems: "center", overflow: "hidden", px: 0, py: 0.25, gap: 1 }}>
              <RankIcon rank={option.rank} />
              <Box sx={{ overflow: "hidden", whiteSpace: "nowrap", textOverflow: "ellipsis" }}>
                <Box component="span" fontWeight="bold" textTransform="uppercase">
                  {option.rank}{option.count ? ` (${option.count})` : ""}
                </Box>
              </Box>
            </Box>
          </ListItemButton>
        </ListItem>
      ))}
    </List>
  </PopoverMenu>
);