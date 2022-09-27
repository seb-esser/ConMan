from pprint import pprint

from scripts import GraphBasedModelDiff
from scripts.GetStatus import get_status
from scripts.GraphBasedModelDiff import diff


def commit():
    ts_guid_dict = get_status()
    pprint(ts_guid_dict)
    all_pairs = []
    for pair in all_pairs:
        diff(pair[0], pair[1])


if __name__ == "__main__":
    commit()
