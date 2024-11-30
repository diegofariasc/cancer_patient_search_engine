from typing import TypeAlias
from string import punctuation
from nltk.corpus import stopwords
from nltk import download
from backend.documentTypes import DocumentLanguage
from nltk import SnowballStemmer

StopwordSetCollection: TypeAlias = dict[DocumentLanguage, set[str]]
StemmerCollection: TypeAlias = dict[DocumentLanguage, SnowballStemmer]


def build_stopword_set_collection() -> StopwordSetCollection:
    download("stopwords")
    stopwords_sets = {
        language: set(stopwords.words(language))
        for language in DocumentLanguage.get_values()
    }

    return stopwords_sets


def build_punctuation_set() -> set[str]:
    download("punkt")
    punctuation_set = set(punctuation)

    return punctuation_set


def build_stemmer_collection() -> StemmerCollection:
    download("stopwords")
    stemmer_collection = {
        language: SnowballStemmer(language)
        for language in DocumentLanguage.get_values()
    }

    return stemmer_collection


def is_stopword(
    word: str, language: DocumentLanguage, stopwords_sets: StopwordSetCollection
) -> bool:
    return word.lower() in stopwords_sets[language]
