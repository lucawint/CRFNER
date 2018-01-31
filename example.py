from configparser import ConfigParser
from datetime import datetime

from src.crf_ner import CRFNER

CONFIG_FILE = 'training_config.ini'
EVAL_FILE = 'data/conll_ned.testa.txt'


print('[i] Starting example.py at {}.'.format(datetime.now()))

cfg = ConfigParser()
cfg.read(CONFIG_FILE)

ner = CRFNER()

ner.train(cfg=cfg)

ner.evaluate(fp=EVAL_FILE)

print('[i] Finished at {}.'.format(datetime.now()))
