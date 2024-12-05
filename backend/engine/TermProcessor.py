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

    def get_terms(self, text: str, language: DocumentLanguage = None):
        text = text.lower()
        tokens = word_tokenize(text)
        language = get_text_language(text, language)

        terms = set(
            [
                self.__stemmer_collection[language].stem(term)
                for term in tokens
                if (
                    term.isalpha()
                    and len(term) > 3
                    and not is_stopword(term, language, self.__stopword_set_collection)
                    and not term in self.__puntuation_set
                )
            ]
        )
        return terms

    def get_term_frequencies(
        self, text: str, language: DocumentLanguage = None
    ) -> dict[str, int]:

        terms = self.get_terms(text, language)
        term_frequencies = {}

        for term in terms:
            if term in term_frequencies:
                term_frequencies[term] += 1
            else:
                term_frequencies[term] = 1

        return term_frequencies
