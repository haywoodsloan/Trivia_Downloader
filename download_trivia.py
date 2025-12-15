import requests
import json
import time
import sys
import os
import html
import shutil

max_size = 500
base_url = "https://opentdb.com/api.php?amount=50&category={number}&difficulty={diff}&token={token}"
difficulties = ["Easy", "Medium", "Hard"]
trivia_categories = {
    "General Knowledge": 9,
    "Books": 10,
    "Film": 11,
    "Music": 12,
    "Musicals & Theatres": 13,
    "Television": 14,
    "Video Games": 15,
    "Board Games": 16,
    "Science & Nature": 17,
    "Computers": 18,
    "Mathematics": 19,
    "Mythology": 20,
    "Sports": 21,
    "Geography": 22,
    "History": 23,
    "Politics": 24,
    "Art": 25,
    "Celebrities": 26,
    "Animals": 27,
    "Vehicles": 28,
    "Comics": 29,
    "Gadgets": 30,
    "Japanese Anime & Manga": 31,
    "Cartoon & Animations": 32,
}


def decode(obj):
    if isinstance(obj, list):
        for index, value in enumerate(obj):
            if isinstance(value, str):
                obj[index] = html.unescape(value)
            else:
                decode(value)
    elif isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str):
                obj[key] = html.unescape(value)
            else:
                decode(value)
    return obj


def trim(obj):
    obj.pop("category", None)
    obj.pop("difficulty", None)
    return obj


if len(sys.argv) < 2:
    raise "Must specify output folder"

token_request = requests.get("https://opentdb.com/api_token.php?command=request")
token = json.loads(token_request.text)["token"]

base_path = sys.argv[1]
for content in os.scandir(base_path):
    if content.is_dir():
        shutil.rmtree(content.path)
    else:
        os.unlink(content.path)

for category, number in trivia_categories.items():
    for difficulty in difficulties:

        results = []
        while len(results) < max_size:
            request_url = base_url.format(number=number, diff=difficulty, token=token)
            response = requests.get(request_url.lower())

            try:
                response.raise_for_status()

                parsed = json.loads(response.text)
                if parsed["response_code"] == 4:
                    time.sleep(5)
                    break
                elif parsed["response_code"] != 0:
                    raise Exception(f"Bad response code: {parsed["response_code"]}")

                results += map(trim, map(decode, parsed["results"]))
            except Exception as e:
                print(e)

            time.sleep(5)

        output_dir = f"{base_path}/{category}/{difficulty}"
        os.makedirs(output_dir, exist_ok=True)

        for index, result in enumerate(results):
            with open(f"{output_dir}/{index}.json", "w", encoding="utf8") as file:
                file.write(json.dumps(result, indent=2, ensure_ascii=False))
