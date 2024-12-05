from backend.engine.utils import (
    build_punctuation_set,
    build_stemmer_collection,
    build_stopword_set_collection,
    is_stopword,
)

from backend.documentTypes import DocumentLanguage
from nltk.tokenize import word_tokenize
from backend.utils import get_text_language


class TermProcessor:
    def __init__(self):
        self.__stopword_set_collection = build_stopword_set_collection()
        self.__puntuation_set = build_punctuation_set()
        self.__stemmer_collection = build_stemmer_collection()

    def get_term_frequencies(
        self, text: str, language: DocumentLanguage = None
    ) -> list[str]:
        text = text.lower()
        tokens = word_tokenize(text)
        language = get_text_language(text, language)

        terms = {}

        for term in tokens:
            if (
                not term.isalpha()
                or len(term) < 3
                or is_stopword(term, language, self.__stopword_set_collection)
                or term in self.__puntuation_set
            ):
                continue

            stemmed_term = self.__stemmer_collection[language].stem(term)

            if stemmed_term in terms:
                terms[stemmed_term] += 1
            else:
                terms[stemmed_term] = 1

        return terms
