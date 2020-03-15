import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles(theme => ({
  root: {
    flexGrow: 1
  },
  paper: {
    padding: theme.spacing(2)
  },
  battleMetrics: {
    position: 'relative',
    marginLeft: 0,
    width: '100%',
    [theme.breakpoints.up('sm')]: {
      marginLeft: theme.spacing(1),
      width: 'auto',
    },
    [theme.breakpoints.down('xs')]: {
      display: "none"
    },
  },
  title: {
    flexGrow: 1,
    display: 'block',
    textAlign: 'left'
  },
  slider: {
    textAlign: "left"
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
  alignLeft: {
    textAlign: "left"
  },
  textLeft: {
    textAlign: "left",
    paddingLeft: theme.spacing(2)
  },
  textRight: {
    textAlign: "right",
    paddingRight: theme.spacing(2)
  },
  textCenter: {
    textAlign: "center"
  },
  padding: {
    padding: theme.spacing(1)
  },
  doublePadding: {
    padding: theme.spacing(2)
  },
  paddingLeft: {
    paddingLeft: theme.spacing(1),
  },
  paddingRight: {
    paddingRight: theme.spacing(1)
  },
  paddingTop: {
    paddingTop: theme.spacing(1)
  },
  paddingBottom: {
    paddingBottom: theme.spacing(1)
  },
  noPaddingMargin: {
    padding: 0,
    margin: 0
  },
  ellipsis: {
    whiteSpace: "nowrap",
    overflow: "hidden",
    textOverflow: "ellipsis",
    '&:hover': {
      whiteSpace: "break-spaces",
      overflowWrap: "anywhere",
      overflow: "visible",
   },
  },
  pagination: {
    '& > ul': {
      justifyContent: "center"
    }
  },
  noPaddingMarginBottom: {
    paddingBottom: 0,
    marginBottom: 0
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
    paddingLeft: 0,
  },
  grow: {
    flexGrow: 1,
  },
  fab: {
    margin: "0px",
    top: "auto",
    right: "20px",
    bottom: "20px",
    left: "auto",
    position: "fixed",
  },
  transferList: {
    height: 600,
    overflow: 'auto',
  },
  transferListButton: {
    margin: theme.spacing(0.5, 0),
  },
  popover: {
    pointerEvents: 'none',
  },
}));

export default useStyles;
