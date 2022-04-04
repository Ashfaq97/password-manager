In order to get the OCR tests to work you need to install both Tesseract and pytesseract the steps for doing so are listed below:

1 Download tesseract exe from https://github.com/UB-Mannheim/tesseract/wiki.

2 Install this exe in C:\Program Files (x86)\Tesseract-OCR

3 Add C:\Program Files (x86)\Tesseract-OCR or C:\Program Files\Tesseract-OCR (for a 64 bit machine) to the PATH environment variable

4 Run pip install pytesseract

5 To test if tesseract is installed type in run pngtest.py in OCR tests if you get no errors then pytesseract works