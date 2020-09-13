import React from "react";
import {
    Grid,
    TextField,
    List,
    ListItem,
    ListItemText,
    ListItemSecondaryAction,
    IconButton,
    Typography,
} from "@material-ui/core";
import DeleteIcon from "@material-ui/icons/Delete";
import AddIcon from "@material-ui/icons/Add";
import CollapseCard from "../collapseCard";
import TextHistory, { getAllNamespaces } from "../textHistory";
import InputLabel from "@material-ui/core/InputLabel";
import FormHelperText from "@material-ui/core/FormHelperText";
import FormControl from "@material-ui/core/FormControl";
import Select from "@material-ui/core/Select";
import NativeSelect from "@material-ui/core/NativeSelect";
import { capitalize } from "lodash";

const SelectNameSpace = ({ value, values, handleChange }) => (
    <FormControl>
        <InputLabel htmlFor="age-native-simple">Category</InputLabel>
        <Select
            native
            style={{ minWidth: '100px' }}
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
        const texts = textHistory.getTexts()


        return (
            <List dense>
                {texts.map((text, idx) => (
                    <ListItem key={idx}>
                        <ListItemText primary={text} />
                        <ListItemSecondaryAction>
                            <IconButton
                                edge="end"
                                aria-label="delete"
                                onClick={() => { textHistory.deleteTextByIdx(idx); this.forceUpdate() }}
                            >
                                <DeleteIcon />
                            </IconButton>
                        </ListItemSecondaryAction>
                    </ListItem>
                ))}
            </List>
        );
    };

}

const TextHistoryManager = ({ classes }) => {
    const [namespace, setNamespace] = React.useState("");
    const nameSpaces = getAllNamespaces();

    return (
        <Grid container>
            <Grid lg={12} className={classes.padding}>
                <Typography variant="h6">Manage text history</Typography>
            </Grid>
            {nameSpaces.length > 0 ?
            <React.Fragment>
                <Grid lg={12}>
                    <SelectNameSpace
                        value={namespace}
                        handleChange={setNamespace}
                        values={nameSpaces}
                    />
                </Grid>
                <Grid xs={12} className={classes.padding}>
                    <TextHistoryList namespace={namespace} />
                </Grid>
            </React.Fragment>
            : 
            <Grid xs={12} className={classes.padding}>No text recorded yet</Grid>
            }
        </Grid>
    );
};

export default TextHistoryManager;
