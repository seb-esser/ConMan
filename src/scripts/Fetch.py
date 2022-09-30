import requests


def fetch():

    base_url = "http://localhost:5000"
    endpoint = "/conman/fetch"

    api_location = base_url + endpoint

    res = requests.get(api_location)
    print("Found most recent PatchBundle entitled > {} <".format(res.content.decode("utf-8") ))


if __name__ == "__main__":
    fetch()
