import requests


URL = "https://contract.mexc.com/api/v1/contract/detail"


def get_all_symbols():

    response = requests.get(URL, timeout=10)

    data = response.json()

    symbols = []

    for contract in data["data"]:

        if contract["quoteCoin"] == "USDT":

            symbols.append(contract["symbol"])

    return sorted(symbols)


if __name__ == "__main__":

    print(get_all_symbols()[:20])
