"""Eyecite processes a document to produce a within-document graph in which links.
This script runs it on the scotus dataset from lex_glue.
"""
import argparse
import itertools
import json
import datasets
import eyecite
from datasets import Dataset


def guess_case_name(text):
    "specific to lex_glue, probably has a suitable case id in first line."
    line = text.splitlines()[0]
    return " ".join(line.strip().split()[0:3])


def e_group(values):
    """
    Jsonify a list of eyecite citations.

    :param values:
    :return:
    """
    r = []
    for value in values:
        (start, end) = value.span()
        text = value.token.data
        groups = value.groups
        groups["type"] = type(value).__name__
        groups["text"] = text
        groups["start"] = start
        groups["end"] = end
        r.append(groups)
    return r


def eyecite_groups(citations):
    """Return the grouped citations form an eyecite doc, in suitable form for JSON.

    :param citations:
    :return: dictopnary representation of resolved groups
    """
    resolved = eyecite.resolve_citations(citations)
    result = [e_group(values) for key, values in resolved.items()]

    return result


def eyecite_citations(citations):
    """Format a set of citations as dictionaries.

    :param citations: all the citations found, including ones that are just '$'
    :return: dictionary representation of all the substantive citations.
    """
    return e_group(citations)


def add_citations(example):
    """
    Calculate citation information for an element of a text dataset/
    :param example:
    :return:
    """
    example["case_id"] = guess_case_name(example["text"])
    try:
        citations = eyecite.get_citations(example["text"])
        resolved = eyecite.resolve_citations(citations)
        s1 = {c.span() for c in citations}
        s2 = {c.span() for group in resolved.values() for c in group}
        s1only = s1.difference(s2)
        s2only = s2.difference(s1)
        r1 = [citation for citation in citations if citation.span() in s1only]
        r2 = [
            citation
            for group in resolved.values()
            for citation in group
            if citation.span() in s2only
        ]

        example["spans"] = json.dumps(eyecite_citations(citations))
        example["groups"] = json.dumps(eyecite_groups(citations))
        # example["s1only"] = json.dumps(e_group(r1))
        # example["s2only"] = json.dumps(e_group(r2))
    except TypeError as e:
        print(e, example["case_id"])
        example["groups"] = "[]"
        example["spans"] = "[]"
    return example

def maker(dataset):
    yield from [add_citations(x) for x in itertools.islice(dataset,200)]
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pile_of_law", action="store_true")
    args = parser.parse_args()
    if args.pile_of_law:


        dataset = datasets.load_dataset("pile-of-law/pile-of-law",
                                        'courtlistener_opinions',
                                        trust_remote_code=True,
                                        split="train",
                                        streaming=True)

        transformed_dataset = Dataset.from_generator(maker(dataset))




    else:
        scotus = datasets.load_dataset("lex_glue", "scotus")
        scotus = scotus.map(add_citations)
        scotus["train"].to_parquet("scotus_eyecite_train.pqt")
        scotus["validation"].to_parquet("scotus_eyecite_validation.pqt")
        scotus["test"].to_parquet("scotus_eyecite_test.pqt")
