import json

with open("eu_ai_output.json") as f:
    articles = json.load(f)

numbers = [a["article_number"] for a in articles]
print(numbers)