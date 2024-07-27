# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
import requests
import pandas as pd
import urllib.parse
import time


def fetch_reviews(appid, api_key, language='english', max_pages=20):
    base_url = f"http://store.steampowered.com/appreviews/{appid}?json=1"
    cursor = '*'  # Initial cursor for the Steam API
    all_reviews = []
    page_count = 0  # Track the number of pages requested
    previous_cursors = set()  # Keep track of previous cursors
    retry_count = 0
    max_retries = 5  # Maximum retries for duplicate cursors

    while page_count < max_pages and retry_count < max_retries:
        encoded_cursor = urllib.parse.quote(cursor)
        print(f"Encoded cursor before request: {encoded_cursor}")

        if cursor in previous_cursors:
            print("Duplicate cursor detected.")
            retry_count += 1
            if retry_count >= max_retries:
                print("Maximum retries reached, stopping.")
                break
            print(f"Retry {retry_count}/{max_retries}...")
            time.sleep(2)  # Wait for a bit before retrying
            continue  # Skip the rest of the loop and retry

        previous_cursors.add(cursor)  # Add the current cursor to the set of seen cursors

        params = {
            'key': api_key,
            'language': language,
            'filter': 'all',
            'day_range': 365,
            'review_type': 'all',
            'purchase_type': 'all',
            'num_per_page': 100,
            'cursor': encoded_cursor,
            'filter_offtopic_activity': 0  # Include off-topic reviews
        }
        print(f"Requesting page {page_count + 1} with cursor: {cursor}")
        response = requests.get(base_url, params=params)
        print(f"Response status code: {response.status_code}")


        if response.status_code != 200:
            print(f"Error fetching reviews: {response.status_code}")
            break

        data = response.json()

        if 'reviews' in data and data['reviews']:
            reviews = data['reviews']
            print(f"Found {len(reviews)} reviews on this page.")
            for review in reviews:
                all_reviews.append({
                    'date_posted': pd.to_datetime(review['timestamp_created'], unit='s'),
                    'recommended': review['voted_up'],
                    'hours_played': review['author']['playtime_forever'] / 60,
                    'review_text': review['review'],
                    'votes_up': review['votes_up'],
                    'votes_funny': review['votes_funny'],
                    'author_game_count': review['author']['num_games_owned'],
                    'author_reviews_count': review['author']['num_reviews'],
                    'comment_count': review['comment_count'],
                    'language': language
                })

            cursor = data['cursor']
            print(f"Cursor for next page: {cursor}")
            page_count += 1
            retry_count = 0  # Reset retry count after successful fetch
        else:
            print("No more reviews found or error in response data.")
            break

        # Wait for 2 seconds before the next request
        print("Waiting for 2 seconds before the next request...")
        time.sleep(2)

    # Convert the list of reviews to a DataFrame
    reviews_df = pd.DataFrame(all_reviews)

    # Drop duplicates based on a subset of columns that uniquely identify a review
    reviews_df = reviews_df.drop_duplicates(subset=['date_posted', 'review_text', 'author_game_count'])

    # Sort the DataFrame by 'date_posted' in ascending order (oldest to newest)
    reviews_df = reviews_df.sort_values(by='date_posted', ascending=True)

    return reviews_df

if __name__ == '__main__':
    # Example usage
    print("这里")
    api_key = ''  # Replace 'YOUR_API_KEY' with your actual Steam API key
    appid = ['358200']  # Example AppID, replace with the AppID you're interested in
    language = 'all'  # Language code
    # Fetch and save reviews
    for i in appid:
        reviews_df = fetch_reviews(i, api_key, language=language, max_pages=20)
        # Adjust max_pages as needed

        if not reviews_df.empty:
            reviews_df.to_excel(f'reviews_{i}_{language}.xlsx', index=False)
            print(f"Saved reviews to 'reviews_{i}_{language}.xlsx'")
        else:
            print("No data to save.")


