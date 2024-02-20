import datetime

import datasets
import eyecite
import eyecite.models
import json


# Eyecite processes a document to produce a within-document graph in which links
# go from one location in the document to another. As far as I can determine the
# links always go from a later position to an earlier one, and reflect the assertion
# that both ends of the link refer to the same case.
#
# This code does not yet capture the full metadata present in the eyecite analysis.


def span_pairs(item):
    match item:
        case dict():
            for k, v in item.items():
                source = span(k)
                for item in v:
                    yield source, span(item)

        case _:
            yield item


def span(item):
    match item:
        case eyecite.models.Resource():
            return span(item.citation)
        case eyecite.models.CitationBase():
            return item.span()


def guess_case_name(text):
    "specific to lex_glue, probably has a suitable case id in first line."
    line = text.splitlines()[0]
    return " ".join(line.strip().split()[0:3])


def eyecite_graph(text):
    citations = eyecite.get_citations(text)
    resolved = eyecite.resolve_citations(citations)
    links = [
        dict(
            target_text=text[target[0] : target[1]],
            target_span=target,
            source_span=text[source[0] : source[1]],
            source=source,
        )
        for target, source in span_pairs(resolved)
        if target != source
    ]
    return json.dumps(links, sort_keys=True, indent=4)


def add_citations(example):
    example["case_id"] = guess_case_name(example["text"])
    try:
        example["spans"] = json.dumps([citation.span() for citation in eyecite.get_citations(example["text"])])
        example["graph"] = eyecite_graph(example["text"])
    except TypeError as e:
        print(e, example["case_id"])
        example["graph"] = "[]"
    return example


if __name__ == "__main__":
    scotus = datasets.load_dataset("lex_glue", "scotus")
    scotus = scotus.map(add_citations)
    scotus["train"].to_parquet("scotus_eyecite_train.pqt")
    scotus["validation"].to_parquet("scotus_eyecite_validation.pqt")
    scotus["test"].to_parquet("scotus_eyecite_test.pqt")
