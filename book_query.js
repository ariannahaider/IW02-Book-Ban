// const fs = require('fs');
// const csv = require('csv-parser');

// const HARDCOVER_API_KEY = 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJIYXJkY292ZXIiLCJ2ZXJzaW9uIjoiOCIsImp0aSI6IjU0OTk4MTNmLTA5ZTYtNDMzMC1iYjc4LWIxMDcyOWU3OTU5NyIsImFwcGxpY2F0aW9uSWQiOjIsInN1YiI6IjMxODUzIiwiYXVkIjoiMSIsImlkIjoiMzE4NTMiLCJsb2dnZWRJbiI6dHJ1ZSwiaWF0IjoxNzQzMDcxOTM5LCJleHAiOjE3NzQ2MDc5MzksImh0dHBzOi8vaGFzdXJhLmlvL2p3dC9jbGFpbXMiOnsieC1oYXN1cmEtYWxsb3dlZC1yb2xlcyI6WyJ1c2VyIl0sIngtaGFzdXJhLWRlZmF1bHQtcm9sZSI6InVzZXIiLCJ4LWhhc3VyYS1yb2xlIjoidXNlciIsIlgtaGFzdXJhLXVzZXItaWQiOiIzMTg1MyJ9LCJ1c2VyIjp7ImlkIjozMTg1M319.BU4ATG3BXEZhxEB_8GMljuZ4f3lJJlNaKee6DimKXw8';
// const CSV_FILE_PATH = 'pen_combined.csv'; // Update with your CSV filename

function formatAuthorName(author) {
    const parts = author.split(", ");
    if (parts.length === 2) {
        return `${parts[1]} ${parts[0]}`; // Convert "Last, First" to "First Last"
    }
    return author; // Return unchanged if already correct
}

// // Read CSV file
// const books = [];
// fs.createReadStream(CSV_FILE_PATH)
//   .pipe(csv())
//   .on('data', (row) => {
//     if (row.Title && row.Author) {
//       books.push({ title: row.Title, author: formatAuthorName(row.Author) });
//     }
//   })
//   .on('end', () => {
//     console.log(`Read ${books.length} books from CSV.`);
    
//     // Construct GraphQL query dynamically
//     const filters = books.map(book => 
//       `{
//         title: { _eq: "${book.title}" }, 
//         contributions: { author: { name: { _eq: "${book.author}" } } }
//       }`
//     ).join(',');

//     const query = `
//     {
//       books(where: { _and: [${filters}] }) {
//         title
//         description
//         cached_tags(path: "Genre")
//         contributions {
//             author {
//                 gender_id
//                 is_bipoc
//                 is_lgbtq
//             }
//         }
//       }
//     }`;

//     console.log("Generated Query:\n", query);

//     // Make API request
//     fetch('https://api.hardcover.app/v1/graphql', {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json',
//         'Authorization': HARDCOVER_API_KEY,
//       },
//       body: JSON.stringify({ query }),
//     })
//     .then(response => response.json())
//     .then(({ data }) => {
//       if (data && data.books) {
//         data.books.forEach(book => {
//           const title = book.title || "No title";
//           const author = book.contributions?.[0]?.author?.name || "Unknown Author";
//           const genres = book.cached_tags?.Genre?.map(tag => tag.tag).join(", ") || "No genres available"; 
          
//           console.log(`Title: ${title}`);
//           console.log(`Author: ${author}`);
//           console.log(`Genres: ${genres}`);
//           console.log("----------");
//         });
//       } else {
//         console.error("No books found.");
//       }
//     })
//     .catch(error => console.error("Error fetching data:", error));
//   });

const fs = require('fs').promises;
const readline = require('readline');
const Papa = require('papaparse');


// Your API key
const HARDCOVER_API_KEY = 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJIYXJkY292ZXIiLCJ2ZXJzaW9uIjoiOCIsImp0aSI6IjU0OTk4MTNmLTA5ZTYtNDMzMC1iYjc4LWIxMDcyOWU3OTU5NyIsImFwcGxpY2F0aW9uSWQiOjIsInN1YiI6IjMxODUzIiwiYXVkIjoiMSIsImlkIjoiMzE4NTMiLCJsb2dnZWRJbiI6dHJ1ZSwiaWF0IjoxNzQzMDcxOTM5LCJleHAiOjE3NzQ2MDc5MzksImh0dHBzOi8vaGFzdXJhLmlvL2p3dC9jbGFpbXMiOnsieC1oYXN1cmEtYWxsb3dlZC1yb2xlcyI6WyJ1c2VyIl0sIngtaGFzdXJhLWRlZmF1bHQtcm9sZSI6InVzZXIiLCJ4LWhhc3VyYS1yb2xlIjoidXNlciIsIlgtaGFzdXJhLXVzZXItaWQiOiIzMTg1MyJ9LCJ1c2VyIjp7ImlkIjozMTg1M319.BU4ATG3BXEZhxEB_8GMljuZ4f3lJJlNaKee6DimKXw8';

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// // Create a readline interface to read the CSV file line by line
// const rl = readline.createInterface({
//   input: fs.createReadStream('pen_combined.csv'), // Replace with your CSV file path
//   output: process.stdout,
//   terminal: false,
// });

// Function to fetch book data
async function fetchBookData(query) {
  try {
    const response = await fetch('https://api.hardcover.app/v1/graphql', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': HARDCOVER_API_KEY,
      },
      body: JSON.stringify({ query }),
    });

    const result = await response.json();
    
    if (result.data && result.data.books) {
      result.data.books.forEach(book => {
        const title = book.title || "No title";
        const author = book.contributions?.[0]?.author?.name || "Unknown Author";
        const genres = book.cached_tags?.Genre?.map(tag => tag.tag).join(", ") || "No genres available";
        
        console.log(`Title: ${title}`);
        console.log(`Author: ${author}`);
        console.log(`Genres: ${genres}`);
        console.log("----------");
      });
    } else {
      console.error("No books found.");
    }
  } catch (error) {
    console.error("Error fetching data:", error);
  }
}

// Function to read and process the CSV file
async function processCSV() {
    try {
      const data = await fs.readFile('pen_combined.csv', {encoding: 'utf8'});
      
      // Parse CSV with PapaParse
      const parsedData = Papa.parse(data, {
        header: true,
        dynamicTyping: true,
        skipEmptyLines: true,
      });
  
      for (const row of parsedData.data) {
        const title = row.Title?.trim() || "No title";
        const author = row.Author?.trim() || "Unknown Author";
  
        if (title !== "No title" && author !== "Unknown Author") {
          const query = `
          {
            books(
              where: {
                _and: [
                  {title: {_eq: "${title}"}},
                  {contributions: {author: {name: {_eq: "${formatAuthorName(author)}"}}}}
                ]
              }
            ) {
              title
              description
              cached_tags(path: "Genre")
              contributions {
                author {
                  gender_id
                  is_bipoc
                  is_lgbtq
                }
              }
            }
          }`;
  
          console.log(query)
          await fetchBookData(query);
          await delay(500); // Delay to prevent rate limiting
        }
      }
  
      console.log("Finished processing CSV.");
    } catch (err) {
      console.error("Error reading CSV file:", err);
    }
  }  
  
  // Run the process
  processCSV();