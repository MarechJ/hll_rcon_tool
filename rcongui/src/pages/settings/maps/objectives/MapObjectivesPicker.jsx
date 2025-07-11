import { minWidth } from "@mui/system";
import { getMapLayerImageSrc, getTacMapImageSrc } from "./helpers";
import { styled } from "@mui/material";

const MapWrapper = styled("div")({
  position: "absolute",
  top: 0,
  left: 0,
  width: "100%",
  height: "100%",
});

const MapImg = styled("img")({
  width: "100%",
  height: "100%",
  touchAction: "none",
});

const MapTitle = styled("div")(({ theme }) => ({
  height: 50,
  display: "grid",
  alignContent: "center",
  justifyItems: "center",
  fontSize: 24,
  fontWeight: "bold",
  border: `1px solid ${theme.palette.divider}`,
  borderBottom: "none",
}));

const ObjectivesGrid = styled("div")({
  position: "relative",
  display: "grid",
  gridTemplateColumns: "repeat(5, 1fr)",
  gridTemplateRows: "repeat(5, 1fr)",
  width: "100%",
  height: "100%",
});

const ObjectivesContainer = styled("div")(({ theme }) => ({
  width: "100%",
  minWidth: "50%",
  maxWidth: theme.breakpoints.values.md,
}));

const InteractiveContainer = styled("div")(({ theme }) => ({
  position: "relative",
  aspectRatio: "1 / 1",
}));

const LoadingOverlay = styled("div")({
  display: "grid",
  alignContent: "center",
  justifyItems: "center",
  fontSize: 32,
  fontWeight: "bold",
  background: "rgba(0, 0, 0, 0.6)",
  gridRowStart: 1,
  gridColumnStart: 1,
  gridColumnEnd: 6,
  gridRowEnd: 6,
});

const ControlButton = styled("button", {
  shouldForwardProp: (props) => props !== "state",
})(({ theme, state }) => ({
  border: "4px ridge black",
  minWidth: 0,
  padding: 0,
  borderRadius: 0,
  opacity: 0.35,
  cursor: "pointer",
  "&:hover": {
    borderStyle: "inset",
  },
  "&:disabled": {
    backgroundImage:
      "repeating-linear-gradient(45deg,#ff7700 0, #ff7700 2px, transparent 0, transparent 50%)",
    backgroundSize: "10px 10px",
    cursor: "no-drop",
    "&:hover": {
      borderStyle: "ridge",
    },
  },
  ...(state === "true" && {
    background: theme.palette.success.main,
    borderStyle: "inset",
    "&:hover": {
      background: theme.palette.success.dark,
    },
  }),
  ...(state === "null" && {
    backgroundImage:
      "repeating-linear-gradient(45deg, #000 0, #000 2px, transparent 0, transparent 50%)",
    backgroundSize: "20px 20px",
    cursor: "no-drop",
  }),
}));

const isButtonUnavailable = (state) => {
  return state === null;
};

const isButtonDisabled = (state, index, map, objectives) => {
  const size = 5;
  const targetIndex = index % size;
  const targetRow = Math.floor(index / size);

  // Is unavailable
  if (isButtonUnavailable(state)) {
    return true;
  }

  // Is selected
  if (state === true) return false;

  // Is unselected
  if (map.map.orientation === "vertical") {
    // but there is another selected in the row
    if (objectives[targetRow].includes(true)) return true;
  } else {
    // but there is another selected in the column
    if (objectives.some((row) => row[targetIndex] === true)) return true;
  }

  return false;
};

export function MapObjectivesPicker({ objectives, map, onClick, loading }) {
  return (
    <ObjectivesContainer>
      <MapTitle>{map.pretty_name}</MapTitle>
      <InteractiveContainer>
        <MapWrapper>
          <MapImg
            src={loading ? getMapLayerImageSrc(map) : getTacMapImageSrc(map)}
            alt=""
            draggable={false}
          />
        </MapWrapper>
        <ObjectivesGrid>
          {loading ? (
            <LoadingOverlay>LOADING...</LoadingOverlay>
          ) : (
            objectives.flat().map((state, index) => {
              return (
                <ControlButton
                  key={`${index}${state}`}
                  onClick={() => onClick(index)}
                  disabled={isButtonDisabled(state, index, map, objectives)}
                  state={`${state}`}
                ></ControlButton>
              );
            })
          )}
        </ObjectivesGrid>
      </InteractiveContainer>
    </ObjectivesContainer>
  );
}
