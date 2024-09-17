import { Button, TextField } from "@mui/material";
import { CustomizedDividers } from "../../views/live";
import AddIcon from '@mui/icons-material/Add';

const MessagesDetail = () => {
  return (
    <>
      <CustomizedDividers />
      <TextField fullWidth placeholder="Broadcast message #1" />
      <TextField fullWidth placeholder="Broadcast message #2" />
      <TextField fullWidth placeholder="Broadcast message #3" />
      <TextField fullWidth placeholder="Broadcast message #4" />
      <Button startIcon={<AddIcon />}>Add</Button>
    </>
  );
};

export default MessagesDetail;
