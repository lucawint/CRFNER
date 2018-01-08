from src.html_helpers import HTMLTokenizer


def test_sample_emails(tagged_email):
    doc = tagged_email
    entities = ['pnr', 'f_no', 'dep_date', 'arr_date',
                'dep_apt', 'arr_apt', 'dep_time', 'arr_time']
    tuples_c_by_c = HTMLTokenizer.inline_to_tuples(doc, entities,
                                                   char_by_char=True)

    tuples_ents = [(c, t) for c, t in tuples_c_by_c if t != 'O']

    assert len(tuples_ents) > 0
