import faker from 'faker';

// a little function to help us with reordering the result
export const reorder = (
  list,
  startIndex,
  endIndex
) => {
  const result = Array.from(list);
  const [removed] = result.splice(startIndex, 1);
  result.splice(endIndex, 0, removed);

  return result;
};

export const getItems = (count) =>
  Array.from({ length: count }, (v, k) => k).map(k => (
    faker.commerce.productName()
    //{
    //id: `Item ${k + 1}`,
   // primary: faker.commerce.productName(),
    //secondary: faker.company.catchPhrase()
  //}
  ));
