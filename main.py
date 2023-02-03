import json
import re

import requests
from bs4 import BeautifulSoup
from furl import furl

FNAME = "data.json"

keyword = input("Enter keyword for search: ").strip().lower()
if not keyword:
    exit(0)

url = f"https://www.opennet.ru/keywords/{keyword}.html"

parsed_url = furl(url)
domain = "{uri.scheme}://{uri.netloc}".format(uri=parsed_url)

resp = requests.get(url)
soup = BeautifulSoup(resp.text, "html.parser")
main_table = soup.find("table", {"width": "80%", "align": "center"})
news_table = main_table.find_all(
    "table",
    {
        "bgcolor": "#B0B190",
        "border": "0",
        "cellpadding": "1",
        "cellspacing": "0",
        "width": "100%",
    },
)[1]
count = news_table.find("font", {"color": "#000088"})
if count is None:
    print("No info was found")
    exit(0)

count = int(re.findall(r"\d+", count.contents[-1])[0])

if count > 15:
    ref = domain + main_table.find("a", {"rel": "nofollow"}).attrs.get("href")
    parsed_ref = furl(ref)
    parsed_ref.args["skip"] = 0
    parsed_ref.args["lines"] = count

    resp = requests.get(parsed_ref.url)
    soup = BeautifulSoup(resp.text, "html.parser")
    main_table = soup.find("table", {"width": "80%", "align": "center"})
    news_table = main_table.find_all(
        "table",
        {
            "bgcolor": "#B0B190",
            "border": "0",
            "cellpadding": "1",
            "cellspacing": "0",
            "width": "100%",
        },
    )[1]

columns = [x.find("a") for x in news_table.find_all("tr")[2:]]
articles = [(domain + x.attrs.get("href"), x.text) for x in columns]
with open(FNAME, "r", encoding="utf-8") as f:
    try:
        data = json.load(f, strict=False)
    except json.decoder.JSONDecodeError:
        data = {}

with open(FNAME, "w+", encoding="utf-8") as f:
    if not data or not data.get(keyword):
        data[keyword] = articles
        print("New data saved")
    else:
        new_articles = [
            x for x in articles if not any(y[0] == x[0] for y in data[keyword])
        ]
        print("You missed this:")
        for arcticle in new_articles:
            data[keyword].append(arcticle)
            print(arcticle[0] + " - " + arcticle[1])
    f.truncate(0)
    json.dump(data, f, ensure_ascii=False, indent=4)
