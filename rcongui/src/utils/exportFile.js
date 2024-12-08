/**
 * Function to export array as a txt file
 * @param {string[]} data 
 * @param {string} filename 
 */
const exportFile = (data, filename) => {
  // Convert the array of strings into a single string with newline characters
  const text = data.join("\n");

  // Create a Blob from the string
  const blob = new Blob([text], { type: "text/plain" });

  // Create a link element
  const link = document.createElement("a");

  // Create a URL for the Blob and set it as the href for the link
  link.href = URL.createObjectURL(blob);

  // Set the download attribute with a filename
  link.download = filename + ".txt";

  // Programmatically click the link to trigger the download
  link.click();

  // Clean up the URL object
  URL.revokeObjectURL(link.href);
};

export default exportFile;
