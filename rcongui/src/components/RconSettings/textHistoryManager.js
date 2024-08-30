import React from "react";
import {
  Grid,
  IconButton,
  List,
  ListItem,
  ListItemSecondaryAction,
  ListItemText,
} from "@material-ui/core";
import DeleteIcon from "@material-ui/icons/Delete";
import TextHistory, { getAllNamespaces } from "../textHistory";
import InputLabel from "@material-ui/core/InputLabel";
import FormControl from "@material-ui/core/FormControl";
import Select from "@material-ui/core/Select";

const SelectNameSpace = ({ value, values, handleChange }) => (
  <FormControl>
    <InputLabel htmlFor="age-native-simple">Category</InputLabel>
    <Select
      native
      style={{ minWidth: "100px" }}
      value={value}
      onChange={(e) => handleChange(e.target.value)}
      inputProps={{
        name: "namespace",
      }}
    >
      <option value="" />
      {values.map((v) => (
        <option value={v}>{v}</option>
      ))}
    </Select>
  </FormControl>
);

class TextHistoryList extends React.Component {
  render() {
    const { namespace } = this.props;
    const textHistory = new TextHistory(namespace);
    const texts = textHistory.getTexts();

    return (
      <List dense>
        {texts.map((text, idx) => (
          <ListItem key={idx}>
            <ListItemText primary={text} />
            <ListItemSecondaryAction>
              <IconButton
                edge="end"
                aria-label="delete"
                onClick={() => {
                  textHistory.deleteTextByIdx(idx);
                  this.forceUpdate();
                }}
              >
                <DeleteIcon />
              </IconButton>
            </ListItemSecondaryAction>
          </ListItem>
        ))}
      </List>
    );
  }
}

const TextHistoryManager = () => {
  const [namespace, setNamespace] = React.useState("");
  const nameSpaces = getAllNamespaces();

  return (
    <Grid container>
      {nameSpaces.length > 0 ? (
        <React.Fragment>
          <Grid lg={12}>
            <SelectNameSpace
              value={namespace}
              handleChange={setNamespace}
              values={nameSpaces}
            />
          </Grid>
          <Grid xs={12}>
            <TextHistoryList namespace={namespace} />
          </Grid>
        </React.Fragment>
      ) : (
        <Grid xs={12}>
          No text recorded yet
        </Grid>
      )}
    </Grid>
  );
};

export default TextHistoryManager;
export { SelectNameSpace };
