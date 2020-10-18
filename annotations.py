#!/usr/bin/env python3

from typing import List, Tuple, Dict, Union

import datetime
import dateparser

import json
import os
import sys

import fire

from rapidfuzz import fuzz
from rapidfuzz import process
from loguru import logger


def load_data(path):
    assert os.path.exists(path)
    logger.info(f"Loading data from {path}")
    with open(path) as f:
        return json.load(f)


def search_by_title(data: dict, title: str, topn: int = 5) -> List[tuple]:
    assert title
    logger.info(f"Searching for title={title}")
    res = []
    title = title.lower()
    for item_id, vals in data["list"].items():
        dest_title = vals.get("resolved_title", "").lower()
        if dest_title:
            score = fuzz.ratio(title, dest_title)
            res.append((score, item_id, vals))
        # if dest_title == title:
        #     score = 100
        #     res.append((score, item_id, vals))
    res = sorted(res, key=lambda x: x[0], reverse=True)[:topn]
    if res and res[0][0] > 95:
        return res[:1]
    return res


def extract_annotations(data: dict) -> List[str]:
    annotations = data.get("annotations", [])
    annotations_sorted = sorted(
        annotations, key=lambda x: dateparser.parse(x["created_at"])
    )
    return [annot["quote"] for annot in annotations_sorted]


def dump_annotations(
    annotations: List[str], title: str, path: str = "data/annotations/"
):
    assert title
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(path, title + ".txt")
    logger.info(f"Dumping annotation to {path}")
    with open(path, "w") as f:
        f.write("\n".join(annotations))


def annotation_dumper(datapath, title):
    data = load_data(datapath)
    matched = search_by_title(data, title)
    if matched:
        vals = matched[0][-1]
        annotations = extract_annotations(vals)
        dump_annotations(annotations, vals.get("resolved_title", title))
    else:
        logger.warning(f"No item found for tile={title}")


def main():
    datapath = "data/export-2020-10-14.json"
    args = sys.argv[1:]
    assert args
    title = " ".join(args)
    annotation_dumper(datapath, title)


if __name__ == "__main__":
    # main()
    fire.Fire(annotation_dumper)
