from src.html_helpers import HTMLTokenizer


def test_sample_emails(tagged_email):
    # TODO
    doc = tagged_email
    entities = ['pnr']
    tuples_c_by_c = HTMLTokenizer.inline_to_tuples(doc, entities,
                                                   char_by_char=True)
    print('a')
