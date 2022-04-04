from PIL import Image
import pytesseract

print('Results from OCR:\n\n')
print(pytesseract.image_to_string('test.png'))