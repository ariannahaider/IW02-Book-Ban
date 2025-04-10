const HARDCOVER_API_KEY = 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJIYXJkY292ZXIiLCJ2ZXJzaW9uIjoiOCIsImp0aSI6IjU0OTk4MTNmLTA5ZTYtNDMzMC1iYjc4LWIxMDcyOWU3OTU5NyIsImFwcGxpY2F0aW9uSWQiOjIsInN1YiI6IjMxODUzIiwiYXVkIjoiMSIsImlkIjoiMzE4NTMiLCJsb2dnZWRJbiI6dHJ1ZSwiaWF0IjoxNzQzMDcxOTM5LCJleHAiOjE3NzQ2MDc5MzksImh0dHBzOi8vaGFzdXJhLmlvL2p3dC9jbGFpbXMiOnsieC1oYXN1cmEtYWxsb3dlZC1yb2xlcyI6WyJ1c2VyIl0sIngtaGFzdXJhLWRlZmF1bHQtcm9sZSI6InVzZXIiLCJ4LWhhc3VyYS1yb2xlIjoidXNlciIsIlgtaGFzdXJhLXVzZXItaWQiOiIzMTg1MyJ9LCJ1c2VyIjp7ImlkIjozMTg1M319.BU4ATG3BXEZhxEB_8GMljuZ4f3lJJlNaKee6DimKXw8';
 
const query = `
{
    books(
        where: {_and: [{title: {_ilike: "Call Me By Your Name"}}, {contributions: {author: {name: {_ilike: ""André Aciman"}}}}]}
        ) {
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
 
fetch('https://api.hardcover.app/v1/graphql', {
    headers: {
        'content-type': 'application/json',
        'authorization': HARDCOVER_API_KEY, // Corrected key format
    },
    body: JSON.stringify({ query }),
    method: 'POST',
})
  .then((response) => response.json())
  .then(({ data }) => {
    if (data && data.books) {
      data.books.forEach(book => {
        const title = book.description || "No description available"; // Ensure description is available
        const author = book.contributions?.[0]?.author?.name || "Unknown Author";
        const genres = book.cached_tags?.Genre?.map(tag => tag.tag).join(", ") || "No genres available"; 
        
        console.log(`Title: ${title}`);
        console.log(`Author: ${author}`);
        console.log(`Genres: ${genres}`);
        console.log("----------");
      });
    } else {
      console.error("No data received.");
    }
  })
  .catch(error => console.error("Error fetching data:", error));