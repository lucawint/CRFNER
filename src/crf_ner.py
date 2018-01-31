import os.path
import pickle
from configparser import ConfigParser

import scipy.stats
from sklearn.metrics import make_scorer
from sklearn.model_selection import RandomizedSearchCV
from sklearn_crfsuite import CRF, metrics

from src.html_helpers import HTMLTokenizer
from src.input_generator import InputGenerator


class CRFNER():
    def __init__(self):
        self.crf = None

    @classmethod
    def from_model(cls, model_dir: str):
        model_fp = os.path.join(model_dir, 'model.pkl')

        with open(model_fp, 'rb') as f:
            ner = pickle.load(f)

        print('[i] Successfully loaded model with parameters:')
        for key, value in list(ner._training_cfg.items('Training inputs')):
            key = key.capitalize()
            key = key.replace('_', ' ')
            print(f'{key}: {value}')
        for key, value in list(ner._training_cfg.items('CRF')):
            key = key.capitalize()
            key = key.replace('_', ' ')
            print(f'{key}: {value}')

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
                '-{}:token.lower()'.format(ctr): sent[pos_l][0].lower(),
                '-{}:token.istitle()'.format(ctr): sent[pos_l][0].istitle(),
                '-{}:token.isupper()'.format(ctr): sent[pos_l][0].isupper()
            })

            pos_l -= 1

        #   -> right direction
        ctr = 0
        pos_r = position + 1
        while pos_r < len(sent) and ctr < right_lookout:
            ctr += 1

            features.update({
                '+{}:token.lower()'.format(ctr): sent[pos_r][0].lower(),
                '+{}:token.istitle()'.format(ctr): sent[pos_r][0].istitle(),
                '+{}:token.isupper()'.format(ctr): sent[pos_r][0].isupper()
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

    def _to_input_features(self, input_fp: str):
        # HTML to tagged tuples, as a generator to save memory
        X_gen = InputGenerator(fp=input_fp, entities=self.entities,
                               c_by_c=self.c_by_c)
        y_gen = InputGenerator(fp=input_fp, entities=self.entities,
                               c_by_c=self.c_by_c)

        # CRF features
        X_train = (CRFNER.sent2features(s, self.lookouts) for s in X_gen)
        y_train = (CRFNER.sent2labels(s) for s in y_gen)

        return X_train, y_train

    def _to_input_features_from_tuples(self, tuples_lst: list):
        # CRF features
        X_train = (CRFNER.sent2features(t, self.lookouts) for t in tuples_lst)
        y_train = (CRFNER.sent2labels(t) for t in tuples_lst)

        return X_train, y_train

    def _save_model(self, model_dir: str):
        dest_fp = os.path.join(model_dir, 'model.pkl')
        print(f'[i] Saving model to {dest_fp} .')

        # Create containing directory if necessary
        os.makedirs(f'{model_dir}', exist_ok=True)

        with open(dest_fp, 'wb') as f:
            pickle.dump(self, f)

    def _optimize(self, cfg):
        input_fp = cfg.get('Training inputs', 'TRAINFILE')
        n_iter = cfg.getint('CRF', 'N_ITER')
        n_jobs = cfg.getint('CRF', 'N_JOBS')
        entities = self.entities

        print(f'\n[i] Beginning training with optimization parameters:'
              f'\nn_iter:\t{n_iter}'
              f'\nn_jobs:\t{n_jobs}\n')

        params_space = {
            'c1': scipy.stats.expon(scale=0.5),
            'c2': scipy.stats.expon(scale=0.05)
        }

        f1_scorer = make_scorer(metrics.flat_f1_score,
                                average='weighted',
                                labels=entities)

        rs = RandomizedSearchCV(self.crf,
                                param_distributions=params_space,
                                n_iter=n_iter,
                                n_jobs=n_jobs,
                                scoring=f1_scorer,
                                verbose=2)

        X_train, y_train = self._to_input_features(input_fp=input_fp)

        # Note: cannot use generators with optimization enabled.
        # Raises a TypeError within the sklearn validation.
        X_train = [x for x in X_train]
        y_train = [y for y in y_train]

        rs.fit(X_train, y_train)

        print('\n[i] Finished training with optimization enabled.')

        self.crf = rs.best_estimator_

    def train(self, cfg: ConfigParser):
        # Store model properties
        entities = cfg.get('Training inputs', 'ENTITIES')
        self.entities = [e.strip() for e in entities.split(',')]
        self.c_by_c = cfg.getboolean('Training inputs', 'CHAR_BY_CHAR')
        self.lookouts = {'left': cfg.getint('Training inputs', 'LEFT_LOOKOUT'),
                         'right': cfg.getint('Training inputs', 'LEFT_LOOKOUT')}
        self._training_cfg = cfg

        # Load training inputs
        input_fp = cfg.get('Training inputs', 'TRAINFILE')
        model_dir = cfg.get('Training inputs', 'MODEL_DIR')
        optimize = cfg.getboolean('CRF', 'OPTIMIZE')
        alg = cfg.get('CRF', 'ALGORITHM')
        min_freq = cfg.getint('CRF', 'MIN_FREQ')
        max_its = cfg.getint('CRF', 'ITERATIONS')
        verbose = cfg.getboolean('CRF', 'VERBOSE')

        # Train
        self.crf = CRF(algorithm=alg,
                       min_freq=min_freq,
                       max_iterations=max_its,
                       verbose=verbose)

        if optimize:
            self._optimize(cfg)
        else:
            print('[i] Beginning training with optimization disabled.')
            X_train, y_train = self._to_input_features(input_fp=input_fp)
            self.crf.fit(X=X_train, y=y_train)
            print('[i] Finished training.')

        self._save_model(model_dir)

    def evaluate(self, fp: str):
        if self.crf is None:
            raise ValueError('No CRF model loaded!')

        print(f'[i] Beginning evaluation on {fp} .')
        X_test, y_test = self._to_input_features(input_fp=fp)

        labels = list(self.crf.classes_)
        labels.remove('O')

        y_pred = self.crf.predict(X_test)

        avgf1 = metrics.flat_f1_score(y_test, y_pred, average='weighted', labels=labels)

        _, y_test = self._to_input_features(input_fp=fp)

        report = metrics.flat_classification_report(
            y_test, y_pred, labels=labels, digits=3
        )

        print(f'\n[i] Weighted average F1: {avgf1}')
        print(f'\n[i] Per-class report:\n{report}')

    def tag_document(self, doc: str):
        if self.crf is None:
            raise ValueError('No CRF model loaded!')

        return self.tag_list_of_docs([doc])[0]

    def tag_list_of_docs(self, docs: list):
        if self.crf is None:
            raise ValueError('No CRF model loaded!')

        tupled_docs = [HTMLTokenizer.inline_to_tuples(doc=doc,
                                                      entities=[],
                                                      char_by_char=self.c_by_c)
                       for doc in docs]

        X, _ = self._to_input_features_from_tuples(tupled_docs)

        y_pred = self.crf.predict(X)

        tokens = [[token for token, _ in doc] for doc in tupled_docs]

        tupled_res = [list(zip(l[0], l[1])) for l in zip([t for t in tokens], y_pred)]

        return [HTMLTokenizer.tuples_to_inline(tuples=t, char_by_char=self.c_by_c)
                for t in tupled_res]

    def tag_from_filepath(self, in_fp: str, out_fp: str = None):
        if self.crf is None:
            raise ValueError('No CRF model loaded!')

        X, _ = self._to_input_features(in_fp)

        y_pred = self.crf.predict(X)

        X = InputGenerator(fp=in_fp, entities=self.entities,
                           c_by_c=self.c_by_c)

        tokens = [[token for token, _ in x] for x in X]

        tupled_res = [list(zip(l[0], l[1])) for l in zip([t for t in tokens], y_pred)]

        tagged = [HTMLTokenizer.tuples_to_inline(tuples=t, char_by_char=self.c_by_c)
                  for t in tupled_res]

        if out_fp is not None:
            with open(out_fp, 'w') as f:
                for t in tagged:
                    f.write(f'{t}\n')
            return

        return tagged
