from configparser import ConfigParser

import pytest

from src.crf_ner import CRFNER


def test_config_parsing(conll_config_fp):
    cfg = ConfigParser()
    cfg.read(conll_config_fp)

    ner = CRFNER()
    assert ner is not None
    assert ner.crf is None


@pytest.mark.skip(reason='Training takes a long time')
def test_conll2002_training(conll_config_fp):
    cfg = ConfigParser()
    cfg.read(conll_config_fp)
    ner = CRFNER()
    ner.train(cfg)
    assert ner.crf.classes_ == ['LOC', 'O', 'ORG', 'PER', 'MISC']


def test_conll2002_eval(conll_model_dir_esp):
    ner = CRFNER.from_model(conll_model_dir_esp)

    # Evaluate
    print('\nResults for train file, tokenizing word by word')
    ner.evaluate(fp='test_files/conll_esp/esp.train_inline.txt')

    print('\nResults for test file a')
    ner.evaluate(fp='test_files/conll_esp/esp.testa_inline.txt')

    print('\nResults for test file b')
    ner.evaluate(fp='test_files/conll_esp/esp.testb_inline.txt')


def test_conll2002_eval_c_by_c(conll_model_dir_esp_c_by_c):
    ner = CRFNER.from_model(conll_model_dir_esp_c_by_c)

    # Evaluate
    print('\nResults for train file, tokenizing char by char')
    ner.evaluate(fp='test_files/conll_esp/esp.train_inline.txt')

    print('\nResults for test file a')
    ner.evaluate(fp='test_files/conll_esp/esp.testa_inline.txt')

    print('\nResults for test file b')
    ner.evaluate(fp='test_files/conll_esp/esp.testb_inline.txt')


def test_tag_document(conll_model_dir_esp):
    doc = 'El Departamento de Seguridad Nacional decidió terminar con el Estatus de Protección Temporal para El Salvador con un período de inactividad de 18 meses, de acuerdo con una fuente familiarizada con la decisión.'

    model = CRFNER.from_model(conll_model_dir_esp)

    expected = 'El <ORG>Departamento de Seguridad Nacional</ORG> decidió terminar con el <ORG>Estatus de Protección Temporal para El Salvador</ORG> con un período de inactividad de 18 meses , de acuerdo con una fuente familiarizada con la decisión.'
    res = model.tag_document(doc)

    assert expected == res


def test_tag_document_c_by_c(conll_model_dir_esp_c_by_c):
    doc = 'White jugó al baloncesto en la Universidad de Kansas antes de participar con su selección en los Juegos Olímpicos de México 1968, ganando la medalla de oro.'

    model = CRFNER.from_model(conll_model_dir_esp_c_by_c)

    expected = '<LOC>White</LOC> jugó al baloncesto en la <ORG>Universidad de Kansas</ORG> antes de participar con su selección en los Juegos Olímpicos de <LOC>México</LOC> 1968, ganando la medalla de oro.'
    res = model.tag_document(doc)

    assert expected == res


def test_tag_list_of_docs(conll_model_dir_esp):
    doc_lst = [
        'El Departamento de Seguridad Nacional decidió terminar con el Estatus de Protección Temporal para El Salvador con un período de inactividad de 18 meses, de acuerdo con una fuente familiarizada con la decisión.',
        'Oprah Winfrey: Nadie tendrá que volver a decir "yo también"',
        'Para el profesor de la Universidad de Columbia, Pedro Freyre, fue "un paso mal dado" que el presidente de EE.UU. hiciera este reconocimiento. El periodista argentino José Benegas dice que "esta jugada" de Donald Trump "tiene que ver con la amenaza iraní".']

    model = CRFNER.from_model(conll_model_dir_esp)

    expected = [
        'El <ORG>Departamento de Seguridad Nacional</ORG> decidió terminar con el <ORG>Estatus de Protección Temporal para El Salvador</ORG> con un período de inactividad de 18 meses , de acuerdo con una fuente familiarizada con la decisión.',
        '<PER>Oprah Winfrey: Nadie</PER> tendrá que volver a decir "yo también"',
        'Para el profesor de la <ORG>Universidad de Columbia</ORG> , <PER>Pedro Freyre</PER> , fue "un paso mal dado" que el presidente de <ORG>EE.UU.</ORG> hiciera este reconocimiento. El periodista argentino <PER>José Benegas</PER> dice que "esta jugada" de <PER>Donald Trump</PER> "tiene que ver con la amenaza iraní".'
    ]

    res = model.tag_list_of_docs(doc_lst)

    assert expected == res


def test_tag_from_filepath(conll_model_dir_esp,
                           temp_filepath):
    doc_lst = [
        'El Departamento de Seguridad Nacional decidió terminar con el Estatus de Protección Temporal para El Salvador con un período de inactividad de 18 meses, de acuerdo con una fuente familiarizada con la decisión.',
        'Oprah Winfrey: Nadie tendrá que volver a decir "yo también"',
        'Para el profesor de la Universidad de Columbia, Pedro Freyre, fue "un paso mal dado" que el presidente de EE.UU. hiciera este reconocimiento. El periodista argentino José Benegas dice que "esta jugada" de Donald Trump "tiene que ver con la amenaza iraní".']

    expected = [
        'El <ORG>Departamento de Seguridad Nacional</ORG> decidió terminar con el <ORG>Estatus de Protección Temporal para El Salvador</ORG> con un período de inactividad de 18 meses , de acuerdo con una fuente familiarizada con la decisión.',
        '<PER>Oprah Winfrey: Nadie</PER> tendrá que volver a decir "yo también"',
        'Para el profesor de la <ORG>Universidad de Columbia</ORG> , <PER>Pedro Freyre</PER> , fue "un paso mal dado" que el presidente de <ORG>EE.UU.</ORG> hiciera este reconocimiento. El periodista argentino <PER>José Benegas</PER> dice que "esta jugada" de <PER>Donald Trump</PER> "tiene que ver con la amenaza iraní".'
    ]

    model = CRFNER.from_model(conll_model_dir_esp)

    in_fp = temp_filepath.new()
    out_fp = temp_filepath.new()

    with open(in_fp, 'w') as inf:
        for s in doc_lst:
            inf.write(f'{s}\n')

    # With out_fp
    res = model.tag_from_filepath(in_fp=in_fp, out_fp=out_fp)
    with open(out_fp, 'r') as outf:
        outf_content = outf.read().split('\n')[:-1]
    assert res is None
    assert outf_content == expected


    # Without out_fp
    res = model.tag_from_filepath(in_fp=in_fp)
    assert res == expected
