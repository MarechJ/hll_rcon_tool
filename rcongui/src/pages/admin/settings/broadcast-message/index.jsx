import React, { useEffect, useMemo, useState } from "react";
import {
  Await,
  defer,
  Link,
  useLoaderData,
  useSubmit,
} from "react-router-dom";
import { cmd } from "@/utils/fetchUtils";
import { ErrorSection } from "@/components/shared/ErrorSection";
import {
  Autocomplete,
  Box,
  Button,
  Paper,
  Skeleton,
  Stack,
  styled,
  TextField,
} from "@mui/material";
import { amber, brown } from "@mui/material/colors";
import "@fontsource/montserrat";
import SplitButton from "@/components/shared/SplitButton";
import AddCommentIcon from "@mui/icons-material/AddComment";
import { TEMPLATE_CATEGORY } from "@/utils/lib";
import { BroadcastFields } from "@/components/shared/BroadcastFields";

const INTENT = {
  APPLY_SINGLE: 0,
  APPLY_ALL: 1,
};

export const loader = async () => {
  const message = await cmd.GET_BROADCAST_MESSAGE();
  const config = await cmd.GET_BROADCAST_CONFIG();
  const templates = cmd.GET_MESSAGE_TEMPLATES({
    params: { category: TEMPLATE_CATEGORY.BROADCAST },
  });
  return defer({ message, config, templates });
};

export const action = async ({ request }) => {
  const payload = await request.json();
  console.log(payload);
  return null;
  //   const result = await cmd.SET_BROADCAST_CONFIG({ payload });
  //   return result;
};

const TemplateSkeleton = () => <Skeleton height={80} />;

const StyledTextField = styled(TextField)(() => ({
  "& .MuiOutlinedInput-root, & .MuiOutlinedInput-notchedOutline": {
    borderRadius: 0,
    borderStyle: "double",
    borderWidth: 4,
    borderColor: brown["800"],
    fontFamily: "Montserrat, Arial, sans-serif",
    fontWeight: 600,
    color: "black",
  },
}));

const WelcomeMessagePage = () => {
  const data = useLoaderData();
  const submit = useSubmit();
  const [message, setMessage] = useState(data.message ?? "");
  const [config, setConfig] = useState(data.config);

  useEffect(() => {
    setMessage(data.message);
    setConfig(data.config)
  }, [data.message, data.config]);

  const handleOnChange = (event) => {
    setMessage(event.target.value);
  };

  const handleApplyClick = (intent) => (e) => {
    const payload = { forward: false };
    if (intent === INTENT.APPLY_ALL) {
      payload.forward = true;
    }
    payload.message = message;
    submit(payload, { method: "post", encType: "application/json" });
  };

  const handleTemplateChange = (e, message) => {
    setMessage(message.content);
  };

  const hasChanges = useMemo(
    () => message !== data.message,
    [message, data.message]
  );

  return (
    <Box sx={{ maxWidth: (theme) => theme.breakpoints.values.md }}>
      <Stack
        component={Paper}
        direction={"row"}
        sx={{ p: 1, mb: 1 }}
        justifyContent={"end"}
        alignItems={"center"}
        gap={1}
      >
        <Button
          component={Link}
          startIcon={<AddCommentIcon />}
          variant="contained"
          to={"/settings/templates/" + TEMPLATE_CATEGORY.BROADCAST.toLowerCase()}
        >
          Create Template
        </Button>
        <SplitButton
          options={[
            {
              name: "Apply",
              buttonProps: {
                disabled: !hasChanges,
                onClick: handleApplyClick(INTENT.APPLY_SINGLE),
              },
            },
            {
              name: "Apply all servers",
              buttonProps: {
                disabled: !hasChanges,
                onClick: handleApplyClick(INTENT.APPLY_ALL),
              },
            },
          ]}
        />
      </Stack>
      <Box sx={{ background: amber["100"], mb: 2 }}>
        <StyledTextField
          name="message"
          value={data.message ?? ""}
          placeholder="Broadcast content"
          fullWidth
          slotProps={{ input: { readOnly: true } }}
          required
        />
      </Box>
      <BroadcastFields message={message ?? ""} onChange={(value) => setMessage(value)} sx={{ mb: 2 }} />
      <React.Suspense fallback={<TemplateSkeleton />}>
        <Await
          resolve={data.templates}
          errorElement={<ErrorSection title={"Welcome Templates"} />}
        >
          {(templates) => {
            return (
              <Autocomplete
                id="template-select"
                fullWidth
                options={templates}
                onChange={handleTemplateChange}
                autoHighlight
                getOptionLabel={(option) => option.title}
                renderOption={(props, option) => {
                  const { key, ...optionProps } = props;
                  return (
                    <Box key={key} component="li" {...optionProps}>
                      #{option.id} {option.title}
                    </Box>
                  );
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Choose a template"
                    slotProps={{
                      htmlInput: {
                        ...params.inputProps,
                      },
                    }}
                  />
                )}
              />
            );
          }}
        </Await>
      </React.Suspense>
    </Box>
  );
};

export default WelcomeMessagePage;
