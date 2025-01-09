import { PopoverMenu } from "@/components/shared/PopoverMenu";
import {
  Tooltip,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Checkbox,
  Box,
  IconButton,
} from "@mui/material";
import ViewColumnIcon from "@mui/icons-material/ViewColumn";

const TableColumnSelection = ({ table, onColumnVisibilityChange }) => {
  const columns = table.getAllColumns().filter((col) => col.getCanHide());

  return (
    <PopoverMenu
      id="column-picker"
      description="Select columns to display"
      renderButton={(props) => (
        <IconButton {...props} size="small" sx={{ borderRadius: 0 }}>
          <Tooltip title="Select columns">
            <ViewColumnIcon sx={{ fontSize: 16 }} />
          </Tooltip>
        </IconButton>
      )}
      sx={{ width: "200px" }}
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
        {columns.map((column) => (
          <ListItem
            key={column.id}
            dense
            disableGutters
            sx={{ "& .MuiButtonBase-root": { opacity: 1 } }}
          >
            <ListItemButton onClick={() => onColumnVisibilityChange(column.id, !column.getIsVisible())}>
              <ListItemIcon>
                <Checkbox
                  edge="start"
                  checked={column.getIsVisible()}
                  disabled={!column.getCanHide()}
                  tabIndex={-1}
                  disableRipple
                  inputProps={{ "aria-labelledby": `picker-${column.id}` }}
                />
              </ListItemIcon>
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  overflow: "hidden",
                  px: 0,
                  py: 0.25,
                  gap: 1,
                }}
              >
                <Box
                  sx={{
                    overflow: "hidden",
                    whiteSpace: "nowrap",
                    textOverflow: "ellipsis",
                  }}
                >
                  <ListItemText id={`picker-${column.id}`}>
                    {column.id}
                  </ListItemText>
                </Box>
              </Box>
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </PopoverMenu>
  );
};

export default TableColumnSelection;
