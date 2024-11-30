from langdetect import detect
from backend.documentTypes import DocumentLanguage


def get_text_language(text: str, language: DocumentLanguage = None) -> DocumentLanguage:
    if language != None:
        return language

    try:
        detected_language = detect(text)
        if detected_language == "es":
            return DocumentLanguage.SPANISH.value
    except:
        pass

    return DocumentLanguage.ENGLISH.value
