// Define the URL of the CSV file to read
const csvUrl = 'data\\ipl_fixtures.csv';

// Fetch the CSV file using the Fetch API
fetch(csvUrl)
  .then(response => response.text())
  .then(csvText => {
    // Parse the CSV text using PapaParse
    const csvData = Papa.parse(csvText).data;

    // Create an HTML table from the CSV data
    const tableHtml = csvData.map(row => {
      return `<tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>`;
    }).join('');

    // Add the HTML table to the page
    document.getElementById('csv-table').innerHTML = tableHtml;
  });