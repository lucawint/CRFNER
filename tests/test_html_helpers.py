from src.html_helpers import HTMLTokenizer, OTHER_ENT_TYPE


def test_nested_inside_simple():
    doc = '<html>Hey, my name is <name>Luca</name>.</html>'
    entities = ['name']
    tuples_c_by_c = HTMLTokenizer.inline_to_tuples(doc, entities,
                                                   char_by_char=True)
    expected = [
        ('<html>', OTHER_ENT_TYPE),
        ('H', OTHER_ENT_TYPE),
        ('e', OTHER_ENT_TYPE),
        ('y', OTHER_ENT_TYPE),
        (',', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('m', OTHER_ENT_TYPE),
        ('y', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('n', OTHER_ENT_TYPE),
        ('a', OTHER_ENT_TYPE),
        ('m', OTHER_ENT_TYPE),
        ('e', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('i', OTHER_ENT_TYPE),
        ('s', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('L', 'name'),
        ('u', 'name'),
        ('c', 'name'),
        ('a', 'name'),
        ('.', OTHER_ENT_TYPE),
        ('</html>', OTHER_ENT_TYPE)
    ]
    assert tuples_c_by_c == expected

    tuples_w_by_w = HTMLTokenizer.inline_to_tuples(doc, entities,
                                                   char_by_char=False)
    expected = [
        ('<html>', OTHER_ENT_TYPE),
        ('Hey', OTHER_ENT_TYPE),
        (',', OTHER_ENT_TYPE),
        ('my', OTHER_ENT_TYPE),
        ('name', OTHER_ENT_TYPE),
        ('is', OTHER_ENT_TYPE),
        ('Luca', 'name'),
        ('.', OTHER_ENT_TYPE),
        ('</html>', OTHER_ENT_TYPE),
    ]
    assert tuples_w_by_w == expected


def test_nested_outside_simple():
    doc = '<html>Hey, my name is <name><strong>Luca</strong></name>.</html>'
    entities = ['name']
    tuples_c_by_c = HTMLTokenizer.inline_to_tuples(doc, entities,
                                                   char_by_char=True)
    expected = [
        ('<html>', OTHER_ENT_TYPE),
        ('H', OTHER_ENT_TYPE),
        ('e', OTHER_ENT_TYPE),
        ('y', OTHER_ENT_TYPE),
        (',', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('m', OTHER_ENT_TYPE),
        ('y', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('n', OTHER_ENT_TYPE),
        ('a', OTHER_ENT_TYPE),
        ('m', OTHER_ENT_TYPE),
        ('e', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('i', OTHER_ENT_TYPE),
        ('s', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('<strong>', OTHER_ENT_TYPE),
        ('L', 'name'),
        ('u', 'name'),
        ('c', 'name'),
        ('a', 'name'),
        ('</strong>', OTHER_ENT_TYPE),
        ('.', OTHER_ENT_TYPE),
        ('</html>', OTHER_ENT_TYPE)
    ]
    assert tuples_c_by_c == expected

    tuples_w_by_w = HTMLTokenizer.inline_to_tuples(doc, entities,
                                                   char_by_char=False)
    expected = [
        ('<html>', OTHER_ENT_TYPE),
        ('Hey', OTHER_ENT_TYPE),
        (',', OTHER_ENT_TYPE),
        ('my', OTHER_ENT_TYPE),
        ('name', OTHER_ENT_TYPE),
        ('is', OTHER_ENT_TYPE),
        ('<strong>', OTHER_ENT_TYPE),
        ('Luca', 'name'),
        ('</strong>', OTHER_ENT_TYPE),
        ('.', OTHER_ENT_TYPE),
        ('</html>', OTHER_ENT_TYPE),
    ]
    assert tuples_w_by_w == expected


def test_nested_inside_10():
    doc = '<html>Hey, my name is ' \
          '<a><b><c><d> <e><f><g><h><i><name>Luca</name></i></h></g>' \
          '</f>.</e></d></c></b></a></html>'
    entities = ['name']
    tuples_c_by_c = HTMLTokenizer.inline_to_tuples(doc, entities,
                                                   char_by_char=True)
    expected = [
        ('<html>', OTHER_ENT_TYPE),
        ('H', OTHER_ENT_TYPE),
        ('e', OTHER_ENT_TYPE),
        ('y', OTHER_ENT_TYPE),
        (',', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('m', OTHER_ENT_TYPE),
        ('y', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('n', OTHER_ENT_TYPE),
        ('a', OTHER_ENT_TYPE),
        ('m', OTHER_ENT_TYPE),
        ('e', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('i', OTHER_ENT_TYPE),
        ('s', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('<a>', OTHER_ENT_TYPE),
        ('<b>', OTHER_ENT_TYPE),
        ('<c>', OTHER_ENT_TYPE),
        ('<d>', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('<e>', OTHER_ENT_TYPE),
        ('<f>', OTHER_ENT_TYPE),
        ('<g>', OTHER_ENT_TYPE),
        ('<h>', OTHER_ENT_TYPE),
        ('<i>', OTHER_ENT_TYPE),
        ('L', 'name'),
        ('u', 'name'),
        ('c', 'name'),
        ('a', 'name'),
        ('</i>', OTHER_ENT_TYPE),
        ('</h>', OTHER_ENT_TYPE),
        ('</g>', OTHER_ENT_TYPE),
        ('</f>', OTHER_ENT_TYPE),
        ('.', OTHER_ENT_TYPE),
        ('</e>', OTHER_ENT_TYPE),
        ('</d>', OTHER_ENT_TYPE),
        ('</c>', OTHER_ENT_TYPE),
        ('</b>', OTHER_ENT_TYPE),
        ('</a>', OTHER_ENT_TYPE),
        ('</html>', OTHER_ENT_TYPE)
    ]
    assert tuples_c_by_c == expected

    tuples_w_by_w = HTMLTokenizer.inline_to_tuples(doc, entities,
                                                   char_by_char=False)
    expected = [
        ('<html>', OTHER_ENT_TYPE),
        ('Hey', OTHER_ENT_TYPE),
        (',', OTHER_ENT_TYPE),
        ('my', OTHER_ENT_TYPE),
        ('name', OTHER_ENT_TYPE),
        ('is', OTHER_ENT_TYPE),
        ('<a>', OTHER_ENT_TYPE),
        ('<b>', OTHER_ENT_TYPE),
        ('<c>', OTHER_ENT_TYPE),
        ('<d>', OTHER_ENT_TYPE),
        ('<e>', OTHER_ENT_TYPE),
        ('<f>', OTHER_ENT_TYPE),
        ('<g>', OTHER_ENT_TYPE),
        ('<h>', OTHER_ENT_TYPE),
        ('<i>', OTHER_ENT_TYPE),
        ('Luca', 'name'),
        ('</i>', OTHER_ENT_TYPE),
        ('</h>', OTHER_ENT_TYPE),
        ('</g>', OTHER_ENT_TYPE),
        ('</f>', OTHER_ENT_TYPE),
        ('.', OTHER_ENT_TYPE),
        ('</e>', OTHER_ENT_TYPE),
        ('</d>', OTHER_ENT_TYPE),
        ('</c>', OTHER_ENT_TYPE),
        ('</b>', OTHER_ENT_TYPE),
        ('</a>', OTHER_ENT_TYPE),
        ('</html>', OTHER_ENT_TYPE),
    ]
    assert tuples_w_by_w == expected


def test_nested_out_and_in():
    doc = '<html><style {whatever}></style>Hey, my name is ' \
          '<name><strong>Luca</strong></name>.</html>'
    entities = ['name']
    tuples_c_by_c = HTMLTokenizer.inline_to_tuples(doc, entities,
                                                   char_by_char=True)
    expected = [
        ('<html>', OTHER_ENT_TYPE),
        ('<style {whatever}>', OTHER_ENT_TYPE),
        ('</style>', OTHER_ENT_TYPE),
        ('H', OTHER_ENT_TYPE),
        ('e', OTHER_ENT_TYPE),
        ('y', OTHER_ENT_TYPE),
        (',', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('m', OTHER_ENT_TYPE),
        ('y', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('n', OTHER_ENT_TYPE),
        ('a', OTHER_ENT_TYPE),
        ('m', OTHER_ENT_TYPE),
        ('e', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('i', OTHER_ENT_TYPE),
        ('s', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('<strong>', OTHER_ENT_TYPE),
        ('L', 'name'),
        ('u', 'name'),
        ('c', 'name'),
        ('a', 'name'),
        ('</strong>', OTHER_ENT_TYPE),
        ('.', OTHER_ENT_TYPE),
        ('</html>', OTHER_ENT_TYPE)
    ]
    assert tuples_c_by_c == expected

    tuples_w_by_w = HTMLTokenizer.inline_to_tuples(doc, entities,
                                                   char_by_char=False)
    expected = [
        ('<html>', OTHER_ENT_TYPE),
        ('<style {whatever}>', OTHER_ENT_TYPE),
        ('</style>', OTHER_ENT_TYPE),
        ('Hey', OTHER_ENT_TYPE),
        (',', OTHER_ENT_TYPE),
        ('my', OTHER_ENT_TYPE),
        ('name', OTHER_ENT_TYPE),
        ('is', OTHER_ENT_TYPE),
        ('<strong>', OTHER_ENT_TYPE),
        ('Luca', 'name'),
        ('</strong>', OTHER_ENT_TYPE),
        ('.', OTHER_ENT_TYPE),
        ('</html>', OTHER_ENT_TYPE),
    ]
    assert tuples_w_by_w == expected


def test_multiple_ent_types():
    doc = '<html>Hey, my name is ' \
          '<name>Luca</name> and I just got back ' \
          'from <location>Colombia</location>.</html>'
    entities = ['name', 'location']
    tuples_c_by_c = HTMLTokenizer.inline_to_tuples(doc, entities,
                                                   char_by_char=True)
    expected = [
        ('<html>', OTHER_ENT_TYPE),
        ('H', OTHER_ENT_TYPE),
        ('e', OTHER_ENT_TYPE),
        ('y', OTHER_ENT_TYPE),
        (',', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('m', OTHER_ENT_TYPE),
        ('y', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('n', OTHER_ENT_TYPE),
        ('a', OTHER_ENT_TYPE),
        ('m', OTHER_ENT_TYPE),
        ('e', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('i', OTHER_ENT_TYPE),
        ('s', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('L', 'name'),
        ('u', 'name'),
        ('c', 'name'),
        ('a', 'name'),
        (' ', OTHER_ENT_TYPE),
        ('a', OTHER_ENT_TYPE),
        ('n', OTHER_ENT_TYPE),
        ('d', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('I', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('j', OTHER_ENT_TYPE),
        ('u', OTHER_ENT_TYPE),
        ('s', OTHER_ENT_TYPE),
        ('t', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('g', OTHER_ENT_TYPE),
        ('o', OTHER_ENT_TYPE),
        ('t', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('b', OTHER_ENT_TYPE),
        ('a', OTHER_ENT_TYPE),
        ('c', OTHER_ENT_TYPE),
        ('k', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('f', OTHER_ENT_TYPE),
        ('r', OTHER_ENT_TYPE),
        ('o', OTHER_ENT_TYPE),
        ('m', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('C', 'location'),
        ('o', 'location'),
        ('l', 'location'),
        ('o', 'location'),
        ('m', 'location'),
        ('b', 'location'),
        ('i', 'location'),
        ('a', 'location'),
        ('.', OTHER_ENT_TYPE),
        ('</html>', OTHER_ENT_TYPE)
    ]
    assert tuples_c_by_c == expected

    tuples_w_by_w = HTMLTokenizer.inline_to_tuples(doc, entities,
                                                   char_by_char=False)
    expected = [
        ('<html>', OTHER_ENT_TYPE),
        ('Hey', OTHER_ENT_TYPE),
        (',', OTHER_ENT_TYPE),
        ('my', OTHER_ENT_TYPE),
        ('name', OTHER_ENT_TYPE),
        ('is', OTHER_ENT_TYPE),
        ('Luca', 'name'),
        ('and', OTHER_ENT_TYPE),
        ('I', OTHER_ENT_TYPE),
        ('just', OTHER_ENT_TYPE),
        ('got', OTHER_ENT_TYPE),
        ('back', OTHER_ENT_TYPE),
        ('from', OTHER_ENT_TYPE),
        ('Colombia', 'location'),
        ('.', OTHER_ENT_TYPE),
        ('</html>', OTHER_ENT_TYPE)
    ]
    assert tuples_w_by_w == expected


def test_double_entity_tag():
    # In case a token is tagged by two entities, the inner tag
    # is chosen as the entity
    doc = '<html>Hey, my name is ' \
          '<first_name><name>Luca</name></first_name> and I just got back ' \
          'from <dest><location>Colombia</location></dest>.</html>'
    entities = ['name', 'first_name', 'location', 'dest']
    tuples_c_by_c = HTMLTokenizer.inline_to_tuples(doc, entities,
                                                   char_by_char=True)
    expected = [
        ('<html>', OTHER_ENT_TYPE),
        ('H', OTHER_ENT_TYPE),
        ('e', OTHER_ENT_TYPE),
        ('y', OTHER_ENT_TYPE),
        (',', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('m', OTHER_ENT_TYPE),
        ('y', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('n', OTHER_ENT_TYPE),
        ('a', OTHER_ENT_TYPE),
        ('m', OTHER_ENT_TYPE),
        ('e', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('i', OTHER_ENT_TYPE),
        ('s', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('L', 'name'),
        ('u', 'name'),
        ('c', 'name'),
        ('a', 'name'),
        (' ', OTHER_ENT_TYPE),
        ('a', OTHER_ENT_TYPE),
        ('n', OTHER_ENT_TYPE),
        ('d', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('I', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('j', OTHER_ENT_TYPE),
        ('u', OTHER_ENT_TYPE),
        ('s', OTHER_ENT_TYPE),
        ('t', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('g', OTHER_ENT_TYPE),
        ('o', OTHER_ENT_TYPE),
        ('t', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('b', OTHER_ENT_TYPE),
        ('a', OTHER_ENT_TYPE),
        ('c', OTHER_ENT_TYPE),
        ('k', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('f', OTHER_ENT_TYPE),
        ('r', OTHER_ENT_TYPE),
        ('o', OTHER_ENT_TYPE),
        ('m', OTHER_ENT_TYPE),
        (' ', OTHER_ENT_TYPE),
        ('C', 'location'),
        ('o', 'location'),
        ('l', 'location'),
        ('o', 'location'),
        ('m', 'location'),
        ('b', 'location'),
        ('i', 'location'),
        ('a', 'location'),
        ('.', OTHER_ENT_TYPE),
        ('</html>', OTHER_ENT_TYPE)
    ]
    assert tuples_c_by_c == expected

    tuples_w_by_w = HTMLTokenizer.inline_to_tuples(doc, entities,
                                                   char_by_char=False)
    expected = [
        ('<html>', OTHER_ENT_TYPE),
        ('Hey', OTHER_ENT_TYPE),
        (',', OTHER_ENT_TYPE),
        ('my', OTHER_ENT_TYPE),
        ('name', OTHER_ENT_TYPE),
        ('is', OTHER_ENT_TYPE),
        ('Luca', 'name'),
        ('and', OTHER_ENT_TYPE),
        ('I', OTHER_ENT_TYPE),
        ('just', OTHER_ENT_TYPE),
        ('got', OTHER_ENT_TYPE),
        ('back', OTHER_ENT_TYPE),
        ('from', OTHER_ENT_TYPE),
        ('Colombia', 'location'),
        ('.', OTHER_ENT_TYPE),
        ('</html>', OTHER_ENT_TYPE)
    ]
    assert tuples_w_by_w == expected
