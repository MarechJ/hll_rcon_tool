import { Suspense, useState } from 'react';
import { Box, Typography, Link, Button } from '@mui/material';
import Skeleton from '@mui/material/Skeleton';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// Only lazy load ReactMarkdown if needed, but keep remarkGfm as regular import
const MarkdownContent = ({ content }) => {
  return (
    <Suspense fallback={<Skeleton variant="text" height={100} />}>
      <Box sx={{ 
        '& a': { 
          color: 'primary.main',
          textDecoration: 'none',
          '&:hover': {
            textDecoration: 'underline',
          }
        },
        '& code': {
          backgroundColor: 'action.hover',
          padding: '2px 4px',
          borderRadius: 1,
          fontSize: '0.875em',
        },
        '& pre': {
          backgroundColor: 'action.hover',
          padding: 2,
          borderRadius: 1,
          overflow: 'auto',
        },
        '& ul, & ol': {
          paddingLeft: 2,
        },
        '& img': {
          maxWidth: '100%',
          height: 'auto',
        },
        '& table': {
          borderCollapse: 'collapse',
          width: '100%',
          '& th, & td': {
            border: '1px solid',
            borderColor: 'divider',
            padding: 1,
          }
        }
      }}>
        <ReactMarkdown 
          children={content}
          remarkPlugins={[remarkGfm]}
          components={{
            h1: ({node, ...props}) => <Typography variant="h5" gutterBottom {...props} />,
            h2: ({node, ...props}) => <Typography variant="h6" gutterBottom {...props} />,
            h3: ({node, ...props}) => <Typography variant="subtitle1" gutterBottom {...props} />,
            p: ({node, ...props}) => <Typography variant="body2" {...props} />,
            a: ({node, ...props}) => <Link {...props} target="_blank" rel="noopener" />,
          }}
        />
      </Box>
    </Suspense>
  );
};

export const ReleaseNotes = ({ release }) => {
  const [open, setOpen] = useState(false);

  return (
    <>
        <Button variant='contained' color='primary' size='small' onClick={() => setOpen(!open)}>
            {open ? 'Hide Release Notes' : 'Show Release Notes'}
        </Button>
        {open && (
            <Box component='section' id='latest-release' sx={{ wordWrap: 'break-word' }}>
                <Typography variant='h6'>Latest Release Notes</Typography>
                <MarkdownContent content={release.body} />
            </Box>
        )}
    </>
  );
}; 
