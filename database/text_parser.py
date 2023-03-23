import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import zipfile
from pypdf import PdfReader
from markdown import markdown
from striprtf.striprtf import rtf_to_text

class Parsex():
    def text(f_path):
        text = ""
        with open(f_path, "r") as f:
            text = f.read()
        return(return_x(text))

    def pdf(f_path):
        reader = PdfReader(f_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return(return_x(text))

    def ebook(f_path):
        text = ""
        t = ""
        book = epub.read_epub(f_path)
        items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
        for i in items:
            soup = BeautifulSoup(i.get_body_content(), "html.parser")
            t = t + "\n".join([para.get_text() for para in soup.find_all("p")])
            text = t
        return(return_x(text))
    
    def md(f_path):
        with open(f_path, "r") as md_file:
            md_text = md_file.read()
            html = markdown(md_text)
            soup = BeautifulSoup(html, features="html.parser")
            text = soup.get_text()
            return(return_x(text))
    
    def docx(f_path):
        with zipfile.ZipFile(f_path, 'r') as unzipped:
            with unzipped.open('word/document.xml') as docu:
                text = BeautifulSoup(docu.read(), 'xml')
        return(return_x(text))
    
    def odt(f_path):
        return Parsex.docx(f_path)
    
    def rtf(f_path):
        rtf = ""
        with open(f_path, "r") as f:
            rtf = f.read()
            text = rtf_to_text(rtf)
        return(return_x(text))

def return_x(text):
    return text if text != None else "Couldn't extract text"