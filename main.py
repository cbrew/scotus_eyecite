import datasets
import eyecite

def eyecite_process(text):
    found_citations = eyecite.get_citations(text)
    linked_text = eyecite.annotate_citations(text,
                                             [[c.span(), "<a>", "</a>"] for c in found_citations])
    return linked_text
def add_citations(example):
    example['citations'] = eyecite_process(example['text'])
    return example

if __name__ == '__main__':
    scotus = datasets.load_dataset('lex_glue','scotus')
    scotus = scotus.map(add_citations)
    scotus['train'].to_parquet("scotus_eyecite_train.pqt")
    scotus['validation'].to_parquet("scotus_eyecite_validation.pqt")
    scotus['test'].to_parquet("scotus_eyecite_test.pqt")
