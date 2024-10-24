import faker from "faker";

// a little function to help us with reordering the result
export const reorder = (list, startIndex, endIndex) => {
  const result = Array.from(list);
  const [removed] = result.splice(startIndex, 1);
  result.splice(endIndex, 0, removed);

  return result;
};

export const getItems = (count) =>
  Array.from({ length: count }, (v, k) => k).map(
    (k) => faker.commerce.productName()
    //{
    //id: `Item ${k + 1}`,
    // primary: faker.commerce.productName(),
    //secondary: faker.company.catchPhrase()
    //}
  );

export const unifiedGamemodeName = (modeName) => {
  switch (modeName) {
    case "control":
    case "phased":
    case "majority":
      return "skirmish";
    default:
      return modeName;
  }
}

export const generateObjectivesGrid = (orientation) => {
  const gridSize = 5;
  const defaultState = false
  const blocked = null;

  const blockedRowTemplate = () => Array(gridSize).fill(blocked);
  const verticalRowTemplate = () => [
    blocked,
    defaultState,
    defaultState,
    defaultState,
    blocked,
  ];
  const horizontalRowTemplate = () => Array(gridSize).fill(defaultState);

  return Array(gridSize)
    .fill(null)
    .map((_, row) => {
      if (orientation === "vertical") {
        return verticalRowTemplate();
      }
      if (row === 0 || row === gridSize - 1) {
        return blockedRowTemplate();
      }
      return horizontalRowTemplate();
    });
};

export const getMapLayerImageSrc = (mapLayer) => `/maps/icons/${mapLayer.image_name}`;
export const getTacMapImageSrc = (mapLayer) => `/tac-maps/${mapLayer.map.id}.webp`;
