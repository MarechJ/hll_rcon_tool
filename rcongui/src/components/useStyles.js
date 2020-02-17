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
  marginRight: {
    marginRight: theme.spacing(1)
  },
  paperLogs: {
    textAlign: "left",
    padding: theme.spacing(2),
  },
  logs: {
    margin: 0,
    whiteSpace: 'pre-wrap'
  },
  logsControl: {
    width: "100%",
    height: "100%",
  },
  textLeft: {
    textAlign: "left",
    paddingLeft: theme.spacing(2)
  },
  textRight: {
    textAlign: "right",
    paddingRight: theme.spacing(2)
  },
  padding: {
    padding: theme.spacing(1)
  },
  menuButton: {
    marginRight: theme.spacing(2),
  },
  appBar: {
    borderBottom: `1px solid ${theme.palette.divider}`,
  },
  link: {
    margin: theme.spacing(1, 1.5),
  },
  firstLink: {
    margin: theme.spacing(1, 1.5),
    marginLeft: 0,
  },
  toolbar: {
    flexWrap: 'wrap',
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
