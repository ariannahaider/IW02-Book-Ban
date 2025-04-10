import requests
import json
import csv
import time

# IW02-bookdata
api_key = 'AIzaSyBXcwyqv8jp7DbKJ5qOGd8HOBKCkKuXLvQ'
#IW02-bookdata-two
# api_key = 'AIzaSyAMdIkjqEV7DI2f_Ar1oWvR0cKpMI2UCME'

def get_volume_ids_by_author_and_title(title, author):
    query = f'intitle:"{title}" + inauthor:"{author}"'
    # Construct the URL with the search query and API key
    url = f'https://www.googleapis.com/books/v1/volumes?q={query}&orderBy=relevance&maxResults=1&key={api_key}'

    # Add a delay between each request to avoid hitting rate limits
    time.sleep(5)

    # Make the API request
    response = requests.get(url)

    if response.status_code == 200:
        # Parse the JSON response
        books_data = response.json()

        # List to store volume IDs
        volume_ids = []

        # Check if 'items' exist in the response (which contains the books)
        if 'items' in books_data:
            # Loop through the books and extract the volume IDs
            for book in books_data['items']:
                volume_id = book.get('id')  # Get the volume ID
                volume_ids.append(volume_id)  # Append the volume ID to the list

        return volume_ids
    else:
        return f"Error: {response.status_code}"
    
# Function to read books from CSV and query Google Books API
def read_books_and_query_csv(file_path):
    volume_ids = []
    
    # Open the CSV file and read the rows
    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)  # Use DictReader to access columns by name
        
        # Loop through each row in the CSV
        for row in csv_reader:
            title = row['Title']
            author = row['Author']

            if ',' in author:
                author = ' '.join(author.split(', ')[::-1])
            
            # Query Google Books API with the title and author
            ids = get_volume_ids_by_author_and_title(title, author)
            volume_ids.extend(ids)
    
    return volume_ids


volume_ids = read_books_and_query_csv('/Users/ariannahaider/Downloads/IW02/pen_short.csv')
# # Print the volume IDs
# print("Volume IDs:", volume_ids)

# List to store all book information
all_book_info = []

for volume_id in volume_ids:
    url = f'https://www.googleapis.com/books/v1/volumes/{volume_id}?key={api_key}'

    # Add a delay between each request to avoid hitting rate limits
    time.sleep(5)

    # Make the API request
    response = requests.get(url)
    
    # Check if the response was successful (status code 200)
    
    if response.status_code == 200:
        # Parse the response as JSON
        book_info = response.json()

        # Append the book information to the list
        all_book_info.append(book_info)
    else:
        print(f"Error: {response.status_code}")

# Save the collected data into a JSON file
output_file_path = 'books_info_4.json'
with open(output_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(all_book_info, json_file, indent=2)

print(f"Data saved to {output_file_path}")