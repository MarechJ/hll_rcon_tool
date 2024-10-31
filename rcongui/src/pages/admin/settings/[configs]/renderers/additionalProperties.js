import {
  getCombinedErrorMessage,
  getErrorTranslator,
  getSubErrorsAt,
  getTranslator,
  mapStateToControlWithDetailProps,
  Resolve,
  update
} from "@jsonforms/core";
import {
  ctxDispatchToControlProps,
  withArrayTranslationProps,
  withJsonFormsContext,
  withTranslateProps
} from "@jsonforms/react";
import React, {useCallback, useMemo, useState} from "react";
import {DeleteDialog, MaterialTableControl} from "@jsonforms/material-renderers";

const objectRenderer = (props) => {
  const [open, setOpen] = useState(false);
  const [path, setPath] = useState(undefined);
  const [rowData, setRowData] = useState(undefined);
  const {removeItems, visible, translations} = props;

  const {
    schema,
    additionalPropertiesSchema,
    rootSchema,
    renderers,
    cells,
    uischema,
    uischemas,
  } = props;

  console.log(props);
  const openDeleteDialog = useCallback(
    (p, rowIndex) => {
      setOpen(true);
      setPath(p);
      setRowData(rowIndex);
    },
    [setOpen, setPath, setRowData]
  );
  const deleteCancel = useCallback(() => setOpen(false), [setOpen]);
  const deleteConfirm = useCallback(() => {
    const p = path.substring(0, path.lastIndexOf('.'));
    removeItems(p, [rowData])();
    setOpen(false);
  }, [setOpen, path, rowData]);
  const deleteClose = useCallback(() => setOpen(false), [setOpen]);

  if (!visible) {
    return null;
  }

  return (
    <>
      <MaterialTableControl
        {...props}
        schema={{
          ...additionalPropertiesSchema,
          ...{
            properties: {
              ...additionalPropertiesSchema.properties,
              ...{key: {description: 'Key', ...schema.propertyNames}},
            }
          },
        }}
        uischema={uischema}
        openDeleteDialog={openDeleteDialog}
        translations={translations}
      />
      <DeleteDialog
        open={open}
        onCancel={deleteCancel}
        onConfirm={deleteConfirm}
        onClose={deleteClose}
        acceptText={translations.deleteDialogAccept}
        declineText={translations.deleteDialogDecline}
        title={translations.deleteDialogTitle}
        message={translations.deleteDialogMessage}
      />
    </>
  );
}

export const withJsonFormsAdditionalPropertiesLayoutProps = (
  Component,
  memoize = true
) => withJsonFormsContext(withContextToAdditionalPropertiesLayoutProps(memoize ? React.memo(Component) : Component));

const withContextToAdditionalPropertiesLayoutProps = (
  Component
) => ({ctx, props}) => {
  const objectLayoutProps = ctxToAdditionalPropertiesLayoutProps(ctx, props);
  const dispatchProps = ctxDispatchToAdditionalPropertiesControlProps(ctx.dispatch);
  return <Component {...props} {...objectLayoutProps} {...dispatchProps} />;
};

export const ctxDispatchToAdditionalPropertiesControlProps = (dispatch) => ({
  ...ctxDispatchToControlProps(dispatch),
  ...useMemo(() => mapDispatchToAdditionalPropertiesControlProps(dispatch), [dispatch]),
});

export const mapDispatchToAdditionalPropertiesControlProps = (dispatch) => ({
  addItem: (path, value) => () => {
    dispatch(
      update(
        path,
        (obj) => {
          if (obj === undefined || obj === null) {
            obj = {};
          }

          obj[''] = value;
          return obj;
        },
        {type: 'ADD', values: [value]}
      )
    );
  },
  removeItems: (path, toDelete) => () => {
    dispatch(
      update(
        path,
        (obj) => {
          console.log(toDelete);
          delete obj[toDelete];
          return obj;
        },
        {type: 'REMOVE', indices: toDelete}
      )
    );
  },
  moveUp: (path, toMove) => () => {
    dispatch(
      update(
        path,
        (obj) => obj,
        {
          type: 'MOVE',
          moves: [{from: toMove, to: toMove - 1}],
        }
      )
    );
  },
  moveDown: (path, toMove) => () => {
    dispatch(
      update(
        path,
        (obj) => obj,
        {
          type: 'MOVE',
          moves: [{from: toMove, to: toMove + 1}],
        }
      )
    );
  },
});

export const ctxToAdditionalPropertiesLayoutProps = (ctx, props) => mapStateToAdditionalPropertiesLayoutProps({jsonforms: {...ctx}}, props);

export const mapStateToAdditionalPropertiesLayoutProps = (state, ownProps) => {
  const {path, schema, uischema, errors, label, ...props} =
    mapStateToControlWithDetailProps(state, ownProps);

  const resolvedSchema = Resolve.schema(schema, 'additionalProperties', props.rootSchema);
  const t = getTranslator()(state);
  const childErrors = getCombinedErrorMessage(
    getSubErrorsAt(path, resolvedSchema)(state),
    getErrorTranslator()(state),
    t,
    undefined,
    undefined,
    undefined
  );

  const allErrors =
    errors +
    (errors.length > 0 && childErrors.length > 0 ? '\n' : '') +
    childErrors;
  return {
    ...props,
    label,
    path,
    uischema,
    schema: schema,
    additionalPropertiesSchema: resolvedSchema,
    data: props.data ? Object.entries(props.data).length : 0,
    errors: allErrors,
  };
};

export const renderer = withJsonFormsAdditionalPropertiesLayoutProps(withTranslateProps(withArrayTranslationProps(objectRenderer)));
