import io
import zipfile
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from app.modules.jobs.exceptions import ParsingError


class BaseJobParser(ABC):
    """Abstract base class defining the job description parsing interface."""

    @abstractmethod
    def parse(self, file_bytes: bytes) -> str:
        """Extract raw text from file bytes. Returns string of parsed text."""
        pass


class DocxJobParser(BaseJobParser):
    """Parser implementation for Microsoft Word DOCX files."""

    def parse(self, file_bytes: bytes) -> str:
        namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                xml_content = z.read('word/document.xml')
                root = ET.fromstring(xml_content)
                
                paragraphs = []
                # Walk through all XML elements to preserve order
                for elem in root.iter():
                    if elem.tag.endswith('p'):
                        texts = [t.text for t in elem.findall('.//w:t', namespaces) if t.text]
                        text_str = ''.join(texts).strip()
                        if text_str:
                            paragraphs.append(text_str)
                    elif elem.tag.endswith('tr'):
                        cells = []
                        for tc in elem.findall('.//w:tc', namespaces):
                            cell_texts = [t.text for t in tc.findall('.//w:t', namespaces) if t.text]
                            cells.append(''.join(cell_texts).strip())
                        cells_str = ' | '.join(c for c in cells if c)
                        if cells_str:
                            paragraphs.append(cells_str)
                            
                return '\n'.join(paragraphs)
        except Exception as e:
            raise ParsingError(f"Failed to parse DOCX document: {str(e)}")


class TxtJobParser(BaseJobParser):
    """Parser implementation for plain text TXT files."""

    def parse(self, file_bytes: bytes) -> str:
        try:
            return file_bytes.decode('utf-8', errors='replace')
        except Exception as e:
            raise ParsingError(f"Failed to parse TXT document: {str(e)}")


class JobParserFactory:
    """Factory creating the appropriate job parser based on extension."""

    @staticmethod
    def get_parser(filename: str) -> BaseJobParser:
        ext = filename.lower().split('.')[-1]
        if ext == 'docx':
            return DocxJobParser()
        elif ext == 'txt':
            return TxtJobParser()
        else:
            raise ParsingError(f"Unsupported file format: {ext}")
