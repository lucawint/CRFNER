from src.html_helpers import HTMLTokenizer


class InputGenerator():
    def __init__(self, fp: str, entities: list,
                 c_by_c: bool):
        self.fp = fp
        self.entities = entities
        self.c_by_c = c_by_c

        self._set_gen()

    def _calculate_length(self):
        with open(self.fp) as f:
            self.length = sum([1 for _ in f])

    def _set_gen(self):
        def gen():
            with open(self.fp) as f:
                for doc in f:
                    yield HTMLTokenizer.inline_to_tuples(
                        doc=doc.strip(),
                        entities=self.entities,
                        char_by_char=self.c_by_c
                        )

        self.gen = gen()

    def __iter__(self):
        return self.gen

    def __next__(self):
        return next(self.gen)

    def __len__(self):
        if self.length is None:
            self._calculate_length()
        return self.length
