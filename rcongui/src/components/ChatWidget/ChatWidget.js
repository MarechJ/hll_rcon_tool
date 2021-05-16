import React, {useEffect, useRef, useState} from "react";
import Badge from "@material-ui/core/Badge";
import {Comment, Send} from "@material-ui/icons";
import {Box, Drawer, Grid, makeStyles, TextField} from "@material-ui/core";
import IconButton from "@material-ui/core/IconButton";
import Typography from "@material-ui/core/Typography";
import moment from "moment";

const useStyles = makeStyles((theme) => ({
    shape: {
        backgroundColor: theme.palette.primary.main,
        width: 48,
        height: 48,
        boxShadow: '1px 2px 8px black',
        borderRadius: '50%'
    },
    chatPosition: {
        position: 'fixed',
        right: '2rem',
        bottom: '2rem',
    },
    commentBox: {
        width: '30rem',
        textAlign: 'right',
        paddingLeft: '2rem',
        paddingTop: '1rem',
        paddingRight: '0.75rem'
    },
    comment: {
        display: 'inline-block',
        backgroundColor: theme.palette.primary.main,
        padding: '2px 10px 2px 10px',
        borderRadius: '10px',
        color: theme.palette.primary.contrastText,
        whiteSpace: 'pre-wrap'
    },
    date: {
        color: theme.palette.disabledTextColor
    },
    textarea: {
        width: '24rem',
        marginBottom: '5px'
    },
}));

const AlwaysScrollToBottom = () => {
    const elementRef = useRef();
    useEffect(() => elementRef.current.scrollIntoView());
    return <div ref={elementRef} />;
};

const ChatWidget = ({data, handleMessageSend}) => {
    const classes = useStyles();
    const [open, setOpen] = useState(false)

    const handleChange = (reason) => {
        if (reason === 'clickaway') {
            return;
        }
        setOpen(!open)
    }

    const handleSubmit = (event) => {
        event.preventDefault();
        handleMessageSend(event.target.message.value)
        event.target.message.value = ''
    }

    return (
        <div className={classes.chatPosition}>
            <Badge color="secondary" overlap="circle" badgeContent={data?.length}>
                <Grid container className={classes.shape}>
                    <IconButton onClick={handleChange}>
                        <Comment style={{color: "white"}}/>
                    </IconButton>
                </Grid>
            </Badge>
            <Drawer anchor='right' open={open} onClose={handleChange}>
                <div className={classes.commentBox} id='messages'>
                    {data?.map((message, index) => {
                        return (
                            <div key={index}>
                                <Typography className={classes.comment}>{message.content}</Typography>
                                <Box color="text.disabled"><Typography >{moment(message.creation_time).format("ddd Do MMM HH:mm:ss")}</Typography></Box>
                            </div>
                        )
                    })}
                    <AlwaysScrollToBottom />
                    <form autoComplete='off' noValidate onSubmit={handleSubmit}>
                        <Grid container justify='space-between'>
                            <TextField
                                id="message"
                                label="Add comment"
                                multiline
                                variant="outlined"
                                className={classes.textarea}
                            />
                            <IconButton style={{height: '48px'}} type="submit" value="submit"><Send color='primary'/></IconButton>
                        </Grid>
                    </form>
                </div>
            </Drawer>
        </div>
    );
}

export default ChatWidget



