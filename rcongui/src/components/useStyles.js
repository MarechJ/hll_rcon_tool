import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles(theme => ({
  root: {
    flexGrow: 1
  },
  paper: {
    padding: theme.spacing(2)
  },
  margin: {
    marginTop: theme.spacing(3)
  },
  marginBottom: {
    marginBottom: theme.spacing(1)
  },
  marginLeft: {
    marginLeft: theme.spacing(1)
  },
  textLeft: {
    textAlign: "left",
    paddingLeft: theme.spacing(2)
  },
  textRight: {
    textAlign: "right",
    paddingRight: theme.spacing(2)
  },
  fab: {
    margin: "0px",
    top: "auto",
    right: "20px",
    bottom: "20px",
    left: "auto",
    position: "fixed",
}
}));

export default useStyles;
