from configparser import ConfigParser

from src.crf_ner import CRFNER


def test_config_parsing(training_config_fp):
    cfg = ConfigParser()
    cfg.read(training_config_fp)

    ner = CRFNER()
    assert ner is not None
    assert ner.crf is None


def test_conll2002_training(config_fp_conll):
    cfg = ConfigParser()
    cfg.read(config_fp_conll)
    ner = CRFNER()
    ner.train(cfg)
    assert ner.crf.classes_ == ['LOC', 'O', 'ORG', 'PER', 'MISC']


def test_conll2002_eval(config_fp_conll):
    cfg = ConfigParser()
    cfg.read(config_fp_conll)
    ner = CRFNER.from_model(cfg.get('Training inputs', 'MODEL_DIR'))
    # Evaluate
    print('\nResults for train file')
    ner.evaluate(cfg,
                 fp='/Users/luca/PycharmProjects/CRFNER/tests/test_files/conll/esp.train_inline.txt')

    print('\nResults for test file a')
    ner.evaluate(cfg,
                 fp='/Users/luca/PycharmProjects/CRFNER/tests/test_files/conll/esp.testa_inline.txt')

    print('\nResults for test file b')
    ner.evaluate(cfg,
                 fp='/Users/luca/PycharmProjects/CRFNER/tests/test_files/conll/esp.testb_inline.txt')
