import React, { useEffect, useMemo, useState } from "react";
import { Await, defer, Link, useLoaderData, useSubmit } from "react-router-dom";
import { cmd } from "@/utils/fetchUtils";
import { ErrorSection } from "@/components/shared/ErrorSection";
import {
  Autocomplete,
  Box,
  Button,
  Paper,
  Skeleton,
  Stack,
  TextField,
} from "@mui/material";
import "@fontsource/montserrat";
import SplitButton from "@/components/shared/SplitButton";
import AddCommentIcon from "@mui/icons-material/AddComment";
import { TEMPLATE_CATEGORY } from "@/utils/lib";

const INTENT = {
  APPLY_SINGLE: 0,
  APPLY_ALL: 1,
};

export const loader = async () => {
  const message = await cmd.GET_WELCOME_MESSAGE();
  const templates = cmd.GET_MESSAGE_TEMPLATES({
    params: { category: TEMPLATE_CATEGORY.WELCOME },
  });
  return defer({ message: message ?? "", templates });
};

export const action = async ({ request }) => {
  const payload = await request.json();
  const result = await cmd.SET_WELCOME_MESSAGE({ payload });
  return result;
};

const TemplateSkeleton = () => <Skeleton height={80} />;

const WelcomeMessagePage = () => {
  const data = useLoaderData();
  const submit = useSubmit();
  const [message, setMessage] = useState(data.message);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setMessage(data.message);
    setLoading(false);
  }, [data.message]);

  const handleOnChange = (event) => {
    setMessage(event.target.value);
  };

  const handleApplyClick = (intent) => (e) => {
    const payload = {
      forward: intent === INTENT.APPLY_ALL,
      // if only space chars, send null
      message: !message.trim() ? null : message,
    };
    submit(payload, { method: "post", encType: "application/json" });
  };

  const handleTemplateChange = (e, message) => {
    setMessage(message.content);
  };

  const hasChanges = useMemo(
    () => message !== data.message,
    [message, data.message]
  );

  const applyDisabled = loading || !hasChanges;

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
          to={"/settings/templates/" + TEMPLATE_CATEGORY.WELCOME.toLowerCase()}
        >
          Create Template
        </Button>
        <SplitButton
          disabled={applyDisabled}
          options={[
            {
              name: loading ? "Loading" : "Apply",
              buttonProps: {
                disabled: applyDisabled,
                onClick: handleApplyClick(INTENT.APPLY_SINGLE),
              },
            },
            {
              name: loading ? "Loading" : "Apply all servers",
              buttonProps: {
                disabled: applyDisabled,
                onClick: handleApplyClick(INTENT.APPLY_ALL),
              },
            },
          ]}
        />
      </Stack>
      <Box sx={{ mb: 2 }}>
        <TextField
          name="message"
          value={message ?? ""}
          onChange={handleOnChange}
          placeholder="Message content"
          multiline
          minRows={16}
          fullWidth
          required
        />
      </Box>

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
