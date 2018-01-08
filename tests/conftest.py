# Fixtures shared by multiple tests as recommended in pytest documentation
import os.path

import pytest

script_dir = os.path.dirname(os.path.abspath(__file__))
TEST_FILES_DIR = os.path.join(script_dir, 'test_files')


@pytest.fixture()
def training_config_fp():
    return os.path.join(TEST_FILES_DIR, 'training_config_sample.ini')


@pytest.fixture()
def config_fp_conll():
    return os.path.join(TEST_FILES_DIR, 'training_conll2002.ini')


@pytest.fixture(params=['tagged_email1.html', 'tagged_email2.html',
                        'tagged_email3.html'])
def tagged_email(request):
    _email_dir = os.path.join(TEST_FILES_DIR, 'emails')
    email_fp = os.path.join(_email_dir, request.param)
    with open(email_fp, 'r', encoding='utf-8') as f:
        yield f.read()
