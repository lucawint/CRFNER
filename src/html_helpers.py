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
    def _inline_to_tuples(entities: list, c_by_c: bool,
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

                    HTMLTokenizer._add_tokens_to_tuples(
                        tuples=curr_tuples,
                        tokens=HTMLTokenizer._tokenize(
                            text_to_tokenize,
                            c_by_c),
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
                        c_by_c=c_by_c,
                        char_iter=char_iter,
                        whole_start_tag=whole_start_tag,
                        override_tag=override_tag
                    )

                    curr_tuples.extend(nested_tuples)
            else:
                if prev_tag_word in UNPROCESSED_TAGS:
                    # Inside of a style or script tag
                    inside = ''
                    tag_end = ''

                    while char != '<':
                        inside += char
                        char = next(char_iter)

                    while char != '>':
                        tag_end += char
                        char = next(char_iter)
                    else:
                        tag_end += char

                    curr_tuples.append((inside, OTHER_ENT_TYPE))
                    curr_tuples.append((tag_end, OTHER_ENT_TYPE))
                else:
                    # Regular text, to be tokenized
                    text_to_tokenize += char

        curr_tokens = HTMLTokenizer._tokenize(text_to_tokenize, c_by_c)
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
        # Removing hyperlinks to reduce dictionary size
        processed = re.sub('href=".+?"', 'href=""', doc)

        return processed

    @classmethod
    def inline_to_tuples(cls, doc: str, entities: list, char_by_char: bool):
        doc = cls._preprocess_doc(doc)

        return cls._inline_to_tuples(entities=entities,
                                     c_by_c=char_by_char,
                                     char_iter=iter(doc)
                                     )

    @staticmethod
    def _tuples_to_inline(tuples: list, c_by_c: bool):
        inline_str = ''
        tuples_iter = iter(tuples)

        def add_entity(token, ent_type, c_by_c: bool,
                       prev_was_entity=False):
            """
            Recursive function for adding entities to the inline string.
            :param token: The entity's current token.
            :param ent_type: Entity type of current token.
            :param c_by_c: Whether to do char by char processing.
            :param prev_was_entity: Whether previous call to this function
                                    in the stack was from this function.
            :return:
            """
            content = []
            curr_str = ''
            orig_ent_type = ent_type
            stopped = False

            if not prev_was_entity:
                curr_str += f'<{orig_ent_type}>'

            while ent_type == orig_ent_type:
                content.append(token)
                try:
                    token, ent_type = next(tuples_iter)
                except StopIteration:
                    stopped = True
                    break

            if c_by_c:
                curr_str += ''.join(content)
                curr_str += f'</{orig_ent_type}>'

                if not stopped:
                    if ent_type == OTHER_ENT_TYPE:
                        curr_str += f'{token}'
                    else:
                        curr_str += f'<{ent_type}>'
                        curr_str += add_entity(token, ent_type, c_by_c,
                                               prev_was_entity=True)
            else:
                curr_str += ' '.join(content)
                curr_str += f'</{orig_ent_type}>'
                if not c_by_c:
                    curr_str += ' '

                if not stopped:
                    if ent_type == OTHER_ENT_TYPE:
                        curr_str += f'{token}'
                        if not c_by_c:
                            curr_str += ' '
                    else:
                        curr_str += f'<{ent_type}>'
                        curr_str += add_entity(token, ent_type, c_by_c,
                                               prev_was_entity=True)

            return curr_str

        # Process tokens tuple by tuple
        for token, ent_type in tuples_iter:
            if ent_type == OTHER_ENT_TYPE:
                if c_by_c:
                    inline_str += f'{token}'
                else:
                    inline_str += f'{token} '
            else:
                inline_str += add_entity(token, ent_type, c_by_c)

        if not c_by_c:
            inline_str = inline_str.rstrip()

        return inline_str

    @classmethod
    def tuples_to_inline(cls, tuples: list, char_by_char: bool):
        return cls._tuples_to_inline(tuples=tuples,
                                     c_by_c=char_by_char)
