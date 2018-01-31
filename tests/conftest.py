"""Fixtures shared by multiple tests as recommended in pytest documentation."""
import os.path
from os import remove
from tempfile import mkstemp

import pytest

script_dir = os.path.dirname(os.path.abspath(__file__))
TEST_FILES_DIR = os.path.join(script_dir, 'test_files')


@pytest.fixture()
def conll_config_fp():
    return os.path.join(TEST_FILES_DIR, 'training_conll2002.ini')


@pytest.fixture()
def conll_model_dir_esp():
    return os.path.join(TEST_FILES_DIR, 'conll_esp/model_w_by_w')

@pytest.fixture()
def conll_model_dir_esp_c_by_c():
    return os.path.join(TEST_FILES_DIR, 'conll_esp/model_c_by_c')


@pytest.fixture(params=['tagged_email1.html', 'tagged_email2.html',
                        'tagged_email3.html'])
def tagged_email(request):
    _email_dir = os.path.join(TEST_FILES_DIR, 'emails')
    email_fp = os.path.join(_email_dir, request.param)
    with open(email_fp, 'r', encoding='utf-8') as f:
        yield f.read()

@pytest.fixture()
def temp_filepath():
    filepaths = []

    class Tempfilepath():
        def new(self):
            fp = mkstemp()[1]
            filepaths.append(fp)
            return fp

    yield Tempfilepath()

    # Cleanup
    for fp in filepaths:
        os.remove(fp)


@pytest.fixture()
def temp_filepath2():
    fp = mkstemp()[1]
    yield fp
    remove(fp)
