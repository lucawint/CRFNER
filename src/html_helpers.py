import re

OTHER_ENT_TYPE = 'O'
SPLIT_CHARS = (' ', '-', '(', ')', '[', ']', ',')
UNPROCESSED_TAGS = ('style', 'script')


class HTMLTokenizer():
    @staticmethod
    def _tokenize(text: str, char_by_char: bool):
        if char_by_char:
            return [c for c in text]

        for c in SPLIT_CHARS:
            text = text.replace(c, f' {c} ')
        return [w.strip() for w in text.split() if len(w.strip()) > 0]

    @staticmethod
    def _add_start_tags_to_tuples(tuples, whole_start_tag, entities):
        if whole_start_tag is not None:
            prev_tag_word = whole_start_tag[0]
            whole_start_tag = ' '.join(whole_start_tag)

            # If tag is an entity tag, we don't want to tokenize it
            if prev_tag_word not in entities:
                tuples.append((f'<{whole_start_tag}>', OTHER_ENT_TYPE))

    @staticmethod
    def _add_tokens_to_tuples(tuples, tokens, entities, tag, override_tag=None):
        if len(tokens) == 0:
            return

        if tag in entities:
            for token in tokens:
                tuples.append((token, tag))
            return
        elif override_tag is not None:
            for token in tokens:
                tuples.append((token, override_tag))
        else:
            for token in tokens:
                tuples.append((token, OTHER_ENT_TYPE))

    @staticmethod
    def _add_end_tags_to_tuples(tuples, tag, entities):
        if tag not in entities and tag is not None:
            tuples.append((f'</{tag}>', OTHER_ENT_TYPE))

    @staticmethod
    def _inline_to_tuples(entities: list, char_by_char: bool,
                          char_iter: iter, whole_start_tag=None,
                          override_tag=None):
        curr_tuples = []
        text_to_tokenize = ''

        prev_tag_word = whole_start_tag[
            0] if whole_start_tag is not None else None
        end_tag = f'/{prev_tag_word}'

        HTMLTokenizer.\
            _add_start_tags_to_tuples(curr_tuples, whole_start_tag, entities)

        for char in char_iter:
            if char == '<':
                # Start of a HTML tag
                whole_start_tag = ''
                next_char = next(char_iter)
                while next_char != '>':
                    whole_start_tag += next_char
                    next_char = next(char_iter)

                whole_start_tag = whole_start_tag.split()

                if len(whole_start_tag) > 0:
                    tag_name = whole_start_tag[0]

                    if end_tag == tag_name:
                        break

                    if tag_name in UNPROCESSED_TAGS:
                        # TODO
                        print(f'Processing unprocessed {tag_name} thing')

                    HTMLTokenizer._add_tokens_to_tuples(
                        tuples=curr_tuples,
                        tokens=HTMLTokenizer._tokenize(
                            text_to_tokenize,
                            char_by_char),
                        tag=prev_tag_word,
                        entities=entities
                    )
                    text_to_tokenize = ''

                    # In case of nested tags inside of entity tag
                    if prev_tag_word is not None:
                        override_tag = prev_tag_word \
                            if prev_tag_word in entities else None

                    nested_tuples = HTMLTokenizer._inline_to_tuples(
                        entities=entities,
                        char_by_char=char_by_char,
                        char_iter=char_iter,
                        whole_start_tag=whole_start_tag,
                        override_tag=override_tag
                    )

                    curr_tuples.extend(nested_tuples)
            else:
                # Regular text, to be tokenized
                text_to_tokenize += char

        curr_tokens = HTMLTokenizer._tokenize(text_to_tokenize, char_by_char)
        HTMLTokenizer._add_tokens_to_tuples(
            curr_tuples,
            curr_tokens,
            entities,
            prev_tag_word,
            override_tag=override_tag
        )

        HTMLTokenizer._add_end_tags_to_tuples(
            curr_tuples,
            prev_tag_word,
            entities
        )

        return curr_tuples

    @staticmethod
    def _preprocess_doc(doc):
        # Close style tags
        doc = re.sub('(?P<unclosed><style.+?>.+?{.+?})', '\g<unclosed></style>', doc)

        # Close script tags
        doc = re.sub('(?P<unclosed><script.+?>.+?{.+?})', '\g<unclosed></script>', doc)

        return doc

    @classmethod
    def inline_to_tuples(cls, doc: str, entities: list, char_by_char: bool):
        doc = cls._preprocess_doc(doc)

        return cls._inline_to_tuples(entities=entities,
                                     char_by_char=char_by_char,
                                     char_iter=iter(doc)
                                     )

    def tuples_to_inline(cls):
        # TODO
        pass
