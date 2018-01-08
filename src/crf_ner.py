import os.path
import pickle
from configparser import ConfigParser

import scipy.stats
from sklearn.metrics import make_scorer
from sklearn.model_selection import RandomizedSearchCV
from sklearn_crfsuite import CRF, metrics

from src.input_generator import InputGenerator


class CRFNER():
    def __init__(self):
        self.crf = None

    @classmethod
    def from_model(cls, model_dir: str):
        ner = cls()

        model_fp = os.path.join(model_dir, 'model.pkl')

        with open(model_fp, 'rb') as f:
            ner.crf = pickle.load(f)

        return ner

    @staticmethod
    def token2features(sent: str, position: int, lookouts: dict):
        left_lookout = lookouts['left']
        right_lookout = lookouts['right']

        token = sent[position][0]

        features = {
            'bias': 1.0,
            'token.lower()': token.lower(),
            'token[-3:]': token[-3:],
            'token[-2:]': token[-2:],
            'token.isupper()': token.isupper(),
            'token.istitle()': token.istitle(),
            'token.isdigit()': token.isdigit(),
        }


        # Lookouts
        #   -> left direction
        ctr = 0
        pos_l = position - 1
        while pos_l > 0 and ctr < left_lookout:
            ctr += 1

            features.update({
                '-{}:word.lower()'.format(ctr): sent[pos_l][0].lower(),
                '-{}:word.istitle()'.format(ctr): sent[pos_l][0].istitle(),
                '-{}:word.isupper()'.format(ctr): sent[pos_l][0].isupper()
            })

            pos_l -= 1

        #   -> right direction
        ctr = 0
        pos_r = position + 1
        while pos_r < len(sent) and ctr < right_lookout:
            ctr += 1

            features.update({
                '+{}:word.lower()'.format(ctr): sent[pos_r][0].lower(),
                '+{}:word.istitle()'.format(ctr): sent[pos_r][0].istitle(),
                '+{}:word.isupper()'.format(ctr): sent[pos_r][0].isupper()
            })

            pos_r += 1

        return features

    @staticmethod
    def sent2features(sent: str, lookouts: dict):
        return [CRFNER.token2features(sent,
                                      position=pos,
                                      lookouts=lookouts)
                for pos in range(len(sent))]

    @staticmethod
    def sent2labels(sent: str):
        return [label for token, label in sent]

    def _to_input_features(self, cfg, input_fp=None):
        # Load params from config file
        fp = cfg.get('Training inputs', 'TRAINFILE')
        entities = cfg.get('Training inputs', 'ENTITIES')
        entities = [e.strip() for e in entities.split(',')]
        c_by_c = cfg.getboolean('Training inputs', 'CHAR_BY_CHAR')
        lookouts = {'left': cfg.getint('Training inputs', 'LEFT_LOOKOUT'),
                    'right': cfg.getint('Training inputs', 'LEFT_LOOKOUT')}

        # For evaluation purposes
        if input_fp is not None:
            fp = input_fp

        # HTML to tagged tuples, as a generator to save memory
        X_gen = InputGenerator(fp=fp, entities=entities,
                               c_by_c=c_by_c)
        y_gen = InputGenerator(fp=fp, entities=entities,
                               c_by_c=c_by_c)

        # CRF features
        X_train = (CRFNER.sent2features(s, lookouts) for s in X_gen)
        y_train = (CRFNER.sent2labels(s) for s in y_gen)

        return X_train, y_train

    def _save_model(self, model_dir: str):
        dest_fp = os.path.join(model_dir, 'model.pkl')

        # Create containing directory if necessary
        os.makedirs(f'{model_dir}', exist_ok=True)

        with open(dest_fp, 'wb') as f:
            pickle.dump(self.crf, f)

    def _optimize(self, cfg):
        n_iter = cfg.getint('CRF', 'N_ITER')
        n_jobs = cfg.getint('CRF', 'N_JOBS')
        labels = cfg.get('Training inputs', 'ENTITIES')
        labels = [l.strip() for l in labels.split()]

        params_space = {
            'c1': scipy.stats.expon(scale=0.5),
            'c2': scipy.stats.expon(scale=0.05)
        }

        f1_scorer = make_scorer(metrics.flat_f1_score,
                                average='weighted',
                                labels=labels)

        rs = RandomizedSearchCV(self.crf,
                                param_distributions=params_space,
                                n_iter=n_iter,
                                n_jobs=n_jobs,
                                scoring=f1_scorer,
                                verbose=2)

        X_train, y_train = self._to_input_features(cfg)

        # Note: cannot use generators with optimization enabled.
        # Raises a TypeError within the sklearn validation.
        X_train = [x for x in X_train]
        y_train = [y for y in y_train]

        print(f'\nBeginning training with optimization parameters'
              f'\nn_iter:\tf{n_iter}'
              f'\nn_jobs:\tf{n_jobs}\n')

        rs.fit(X_train, y_train)

        print('\nFinished training with optimization parameters')

        self.crf = rs.best_estimator_

    def train(self, cfg: ConfigParser):
        model_dir = cfg.get('Training inputs', 'MODEL_DIR')
        optimize = cfg.getboolean('CRF', 'OPTIMIZE')
        alg = cfg.get('CRF', 'ALGORITHM')
        min_freq = cfg.getint('CRF', 'MIN_FREQ')
        max_its = cfg.getint('CRF', 'ITERATIONS')
        verbose = cfg.getboolean('CRF', 'VERBOSE')

        self.crf = CRF(algorithm=alg,
                       min_freq=min_freq,
                       max_iterations=max_its,
                       verbose=verbose)

        if optimize:
            self._optimize(cfg)
        else:
            print('[ i ] Beginning training with optimization disabled.')
            X_train, y_train = self._to_input_features(cfg)
            self.crf.fit(X=X_train, y=y_train)
            print('[ i ] Finished training.')

        self._save_model(model_dir)

    def evaluate(self, cfg: ConfigParser, fp: str):
        if self.crf is None:
            raise ValueError('No CRF model loaded!')

        X_test, y_test = self._to_input_features(cfg, input_fp=fp)

        labels = list(self.crf.classes_)
        labels.remove('O')

        y_pred = self.crf.predict(X_test)

        avgf1 = metrics.flat_f1_score(y_test, y_pred, average='weighted', labels=labels)

        _, y_test = self._to_input_features(cfg, input_fp=fp)

        report = metrics.flat_classification_report(
            y_test, y_pred, labels=labels, digits=3
        )

        print(f'\n[ i ] Weighted average F1: {avgf1}')
        print(f'\n[ i ] Per-class report:\n{report}')
