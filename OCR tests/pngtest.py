import pytesseract
from PIL import Image
from spellchecker import SpellChecker

def spellcheck(words):
    spellchecker = SpellChecker()

    misspelled = spellchecker.unknown(words)
    corrected_words = []

    for word in words:
        if word in misspelled:
           corrected_words.append(spellchecker.correction(word))
    
    return " ".join(corrected_words)

print('Results from OCR:\n\n')
print(pytesseract.image_to_string('login page.png'))