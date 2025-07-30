import requests
from bs4 import BeautifulSoup

def get_valuation(stamp_desc):
    url = f"https://www.ebay.com/sch/i.html?_nkw={stamp_desc}&_sop=13&LH_Sold=1"
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(resp.text, "html.parser")
    prices = []
    for price in soup.select(".s-item__price"):
        try:
            p = float(price.text.replace("$", "").replace(",", ""))
            prices.append(p)
        except ValueError:
            continue
    return sum(prices)/len(prices) if prices else 0
