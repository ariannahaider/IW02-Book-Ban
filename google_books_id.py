import requests
import json
import csv
import time

# IW02-bookdata
api_key = 'AIzaSyBXcwyqv8jp7DbKJ5qOGd8HOBKCkKuXLvQ'
#IW02-bookdata-two
# api_key = 'AIzaSyAMdIkjqEV7DI2f_Ar1oWvR0cKpMI2UCME'
#IW02-bookdata-three
# api_key = 'AIzaSyCYScJWj_qmlNxGPXRLCQxtbNcRAFS11QU'


volume_ids = ["w9RXDwAAQBAJ","_QnTtQEACAAJ",""]

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