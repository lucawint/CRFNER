from src.html_helpers import HTMLTokenizer

_entities = ['pnr', 'f_no', 'dep_date', 'arr_date',
             'dep_apt', 'arr_apt', 'dep_time', 'arr_time']

def test_sample_emails(tagged_email):
    doc = tagged_email
    tuples_c_by_c = HTMLTokenizer.inline_to_tuples(doc, _entities,
                                                   char_by_char=True)

    tuples_ents = [(c, t) for c, t in tuples_c_by_c if t != 'O']

    assert len(tuples_ents) > 0
