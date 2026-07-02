import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

def docx_to_txt(docx_path: Path) -> str:
    """Extracts text from a docx file's word/document.xml using standard libraries."""
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }
    
    try:
        with zipfile.ZipFile(docx_path) as z:
            xml_content = z.read('word/document.xml')
            root = ET.fromstring(xml_content)
            
            paragraphs = []
            # Find all paragraphs (p) or tables
            for elem in root.iter():
                if elem.tag.endswith('p'):
                    # Gather all text in this paragraph
                    texts = [t.text for t in elem.findall('.//w:t', namespaces) if t.text]
                    paragraphs.append(''.join(texts))
                elif elem.tag.endswith('tr'):
                    # Row in a table
                    cells = []
                    for tc in elem.findall('.//w:tc', namespaces):
                        cell_texts = [t.text for t in tc.findall('.//w:t', namespaces) if t.text]
                        cells.append(''.join(cell_texts))
                    if cells:
                        paragraphs.append(' | '.join(cells))
            
            return '\n'.join(paragraphs)
    except Exception as e:
        return f"Error extracting text from {docx_path.name}: {str(e)}"

def main():
    src_dir = Path(r"C:\Users\ANKIT PARIDA\Downloads\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge")
    dest_dir = Path(r"a:\Project\Aura-AI\Aura-AI\docs")
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    for docx_file in src_dir.glob("*.docx"):
        txt = docx_to_txt(docx_file)
        out_name = docx_file.stem + ".md"
        out_path = dest_dir / out_name
        out_path.write_text(txt, encoding="utf-8")
        print(f"Converted {docx_file.name} -> {out_name}")

if __name__ == "__main__":
    main()
