#!/usr/bin/env python3

from typing import List, Tuple, Dict, Union

import datetime
import dateparser

import json
import os
import pathlib
import sys

import fire

from rapidfuzz import fuzz
from rapidfuzz import process
from loguru import logger

from newspaper import Article


def get_full_text(url):
    logger.info(f"Extracting information from url={url}")
    article = Article(url)
    article.download()
    article.parse()
    return article.text


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
    url = data.get("resolved_url", "given_url")
    final_annotations = []
    try:
        fulltext = get_full_text(url)
        fulltext_l = fulltext.lower()
        annotations = data.get("annotations", [])

        logger.info("Sorting annotations by position...")
        annotations_text = map(lambda x: x["quote"], annotations)
        annotations_text = list(filter(lambda x: len(x) > 0, annotations_text))
        annotations_indexed = list(
            map(lambda x: (x, fulltext_l.index(x[:20].lower())), annotations_text)
        )
        annotations_indexed = set(annotations_indexed)
        final_annotations = [
            a[0] for a in sorted(annotations_indexed, key=lambda x: x[1])
        ]
    except Exception as e:
        logger.warning(str(e))
        logger.info("Sorting annotations by timestamp...")
        annotations_sorted = sorted(
            annotations, key=lambda x: dateparser.parse(x["created_at"])
        )
        final_annotations = [annot["quote"] for annot in annotations_sorted]
    return dict(url=url, annotations=final_annotations)


def dump_annotations(
    annotations: List[str], title: str, url=None, path: str = "data/annotations/"
):
    assert title
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(path, title + ".txt")
    logger.info(f"Dumping annotation to {path}")
    with open(path, "w") as f:
        if url:
            f.write(url)
            f.write("\n")
            f.write("\n")
        f.write("\n".join(annotations))


def annotation_dumper(
    datapath=pathlib.Path(__file__).parent.absolute().joinpath("data/sync.json"),
    title="",
):
    data = load_data(datapath)
    assert title
    matched = search_by_title(data, title)
    if matched:
        vals = matched[0][-1]
        annotations = extract_annotations(vals)
        dump_annotations(
            annotations=annotations.get("annotations", []),
            title=vals.get("resolved_title", title),
            url=annotations.get("url", None),
        )
    else:
        logger.warning(f"No item found for tile={title}")


def main():
    datapath = "data/sync.json"
    args = sys.argv[1:]
    assert args
    title = " ".join(args)
    annotation_dumper(datapath, title)


if __name__ == "__main__":
    # main()
    fire.Fire(annotation_dumper)
