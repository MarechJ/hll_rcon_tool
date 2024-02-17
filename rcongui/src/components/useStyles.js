import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles((theme) => {
  return {
    root: {
      flexGrow: 1,
    },
    high: {
      color: theme.palette.secondary.main,
    },
    mid: {
      color: theme.palette.error.main,
    },
    low: {
      color: theme.palette.warning.main,
    },
    paper: {
      padding: theme.spacing(2),
    },
    battleMetrics: {
      position: "relative",
      marginLeft: 0,
      width: "100%",
      [theme.breakpoints.up("sm")]: {
        marginLeft: theme.spacing(1),
        width: "auto",
      },
      [theme.breakpoints.down("xs")]: {
        display: "none",
      },
    },
    paddingXs: {
      [theme.breakpoints.down("xs")]: {
        paddingTop: theme.spacing(2),
      },
    },
    title: {
      flexGrow: 1,
      display: "block",
      textAlign: "left",
    },
    loading: {
      height: "200px",
    },
    slider: {
      textAlign: "left",
    },
    margin: {
      marginTop: theme.spacing(3),
    },
    marginTop: {
      marginTop: theme.spacing(1),
    },
    marginBottom: {
      marginBottom: theme.spacing(1),
    },
    marginLeft: {
      marginLeft: theme.spacing(1),
    },
    marginRight: {
      marginRight: theme.spacing(1),
    },
    paperLogs: {
      textAlign: "left",
      padding: theme.spacing(2),
    },
    // from discord_chat.py...
    // RED = 0xA62019
    // LIGHT_RED = 0xF93A2F
    // BLUE = 0x006798 : hsl(199, 100%, 30%)
    // try for better contrast on dark mode : hsl(199, 100%, 40%)
    // BLUE = 0x008bcc
    // LIGHT_BLUE = 0x0099E1 : hsl(199, 100%, 43%)
    // GREEN = 0x07DA63
    logs: {
      margin: 0,
      whiteSpace: "pre-wrap",
    },
    logsChatAxis: {
      color: "#F93A2F",
      margin: 0,
      whiteSpace: "pre-wrap",
    },
    logsChatAllies: {
      color: "#008bcc",
      margin: 0,
      whiteSpace: "pre-wrap",
    },
    logsAdmin: {
      color: "grey",
      margin: 0,
      whiteSpace: "pre-wrap",
    },
    logsTK: {
      color: "grey",
      margin: 0,
      whiteSpace: "pre-wrap",
    },
    logsMatch: {
      color: "grey",
      margin: 0,
      whiteSpace: "pre-wrap",
    },
    logsVote: {
      color: "grey",
      margin: 0,
      whiteSpace: "pre-wrap",
    },
    logsMessage: {
      color: "grey",
      margin: 0,
      whiteSpace: "pre-wrap",
    },
    logsTeamKill: {
      color: "mediumvioletred",
      fontWeight: "bold",
      margin: 0,
      whiteSpace: "pre-wrap",
    },
    logsKill: {
      color: "grey",
      margin: 0,
      whiteSpace: "pre-wrap",
    },
    logsTeamSwitch: {
      color: "grey",
      margin: 0,
      whiteSpace: "pre-wrap",
    },
    logsDisconnected: {
      color: "grey",
      margin: 0,
      whiteSpace: "pre-wrap",
    },
    logsConnected: {
      color: "grey",
      margin: 0,
      whiteSpace: "pre-wrap",
    },
    logsControl: {
      width: "100%",
      height: "100%",
    },
    alignLeft: {
      textAlign: "left",
    },
    textLeft: {
      textAlign: "left",
      paddingLeft: theme.spacing(2),
    },
    textRight: {
      textAlign: "right",
      paddingRight: theme.spacing(2),
    },
    textCenter: {
      textAlign: "center",
    },
    padding: {
      padding: theme.spacing(1),
    },
    gridContainer: {
      width: '100%',
      margin: 0,
    },
    doublePadding: {
      padding: theme.spacing(2),
    },
    doublePaddingBottom: {
      paddingBottom: theme.spacing(2),
    },
    doublePaddingLeft: {
      paddingLeft: theme.spacing(2),
    },
    paddingLeft: {
      paddingLeft: theme.spacing(1),
    },
    paddingRight: {
      paddingRight: theme.spacing(1),
    },
    paddingTop: {
      paddingTop: theme.spacing(1),
    },
    paddingBottom: {
      paddingBottom: theme.spacing(1),
    },
    noPaddingMargin: {
      padding: 0,
      margin: 0,
    },
    helpText: {
      color: theme.palette.text.disabled,
    },
    ellipsis: {
      textAlign: "left",
      whiteSpace: "nowrap",
      overflow: "hidden",
      textOverflow: "ellipsis",
      "&:hover": {
        whiteSpace: "break-spaces",
        overflowWrap: "anywhere",
        overflow: "visible",
      },
    },
    pagination: {
      "& > ul": {
        justifyContent: "center",
      },
    },
    noPaddingMarginBottom: {
      paddingBottom: 0,
      marginBottom: 0,
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
      flexWrap: "wrap",
      paddingLeft: 0,
      //width: 'fit-content',

      "& hr": {
        border: `1px solid black`, // ${theme.palette.divider}`,
        margin: theme.spacing(0, 0.5),
      },
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
      overflow: "auto",
    },
    transferListButton: {
      margin: theme.spacing(0.5, 0),
    },
    popover: {
      pointerEvents: "none",
    },
    divider: {
      width: "100%",
      backgroundColor: theme.palette.background.paper,
    },
    inlineFormControl: {
      margin: theme.spacing(1),
      minWidth: 120,
      display: "inline",
    },
    selectEmpty: {
      marginTop: theme.spacing(2),
    },
    alignRight: {
      textAlign: "right",
    },
  };
});

export default useStyles;
