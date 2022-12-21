import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from consts import SLEEP, TABELOG_URL


def main():
    print("TABELOG URL:", TABELOG_URL)

    page = 1
    while True:
        print(f"fetching page {page}...")
        url = TABELOG_URL.format(page=page)
        r = fetch(url)

        soup = BeautifulSoup(r.content, "html.parser")
        res = parse_page(soup)
        df = pd.DataFrame(res)
        df.to_csv(f"data/page_{page}.csv", index=False)
        print("done.")

        page += 1
        time.sleep(SLEEP)


@retry(wait=wait_exponential(multiplier=1, min=1), stop=stop_after_attempt(3))
def fetch(url):
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        raise RuntimeError("Status code is not ok")
    return r


def parse_page(soup):
    div_list = soup.find_all("div", class_="list-rst__rst-data")

    results = []
    for div in div_list:
        res = parse_restaurant(div)
        results.append(res)

    return results


def parse_restaurant(soup):
    result = {}

    # バッジ
    result["badges"] = []
    for badges in soup.find_all("div", class_="list-rst__award-tooltip"):
        result["badges"].append(badges.p.text.strip())

    # 名前
    result["name"] = soup.find("a", class_="list-rst__rst-name-target").text.strip()

    # エリア・ジャンル
    area_genre = soup.find("div", class_="list-rst__area-genre").text.strip()
    area, genre = area_genre.split("/")
    result["area"] = area.strip()
    result["genres"] = [x.strip() for x in genre.split("、")]

    # レーティング
    result["rating"] = soup.find("span", class_="list-rst__rating-val").text.strip()

    # 昼の予算
    result["price_lunch"] = soup.find(
        "i", class_="c-rating-v3__time--lunch"
    ).next_sibling.text.strip()

    # 夜の予算
    result["price_dinner"] = soup.find(
        "i", class_="c-rating-v3__time--dinner"
    ).next_sibling.text.strip()

    # 定休日
    regular_holiday = soup.find("span", class_="list-rst__holiday-text")
    result["regular_holiday"] = (
        None if regular_holiday is None else regular_holiday.text.strip()
    )

    return result


def save(soup, filepath):
    with open(filepath, "wt") as file:
        file.write(str(soup))


if __name__ == "__main__":
    main()
