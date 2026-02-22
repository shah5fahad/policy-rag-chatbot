from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import asyncio, PyPDF2, re, os
from concurrent.futures import ThreadPoolExecutor
from docx import Document as DocxDocument
from dotenv import load_dotenv
from PIL import Image
import pytesseract

load_dotenv()


CHUNK_SIZE = int(os.getenv("DOCUMENT_CHUNK_SIZE", 1000))  # Number of words per chunk for text splitting

class DocumentParser(ABC):
    """Base abstract class for document parsers."""
    
    @abstractmethod
    async def parse(self, file_path: str) -> Dict[str, Any]:
        """Parse document and return extracted content."""
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """Return list of supported file extensions."""
        pass


class TextParser(DocumentParser):
    """Parser for plain text files."""
    
    async def parse(self, file_path: str) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            content = await loop.run_in_executor(
                executor,
                self._parse_sync,
                file_path
            )
        return content
    
    def _parse_sync(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return {
            "text": text,
            "chunks": self._chunk_text(text),
            "metadata": {"char_count": len(text), "word_count": len(text.split())}
        }
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks for embedding."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), CHUNK_SIZE):
            chunk = ' '.join(words[i:i+CHUNK_SIZE])
            chunks.append(chunk)
        return chunks
    
    def get_supported_extensions(self) -> List[str]:
        return ['txt', 'md']


class PDFParser(DocumentParser):
    """Parser for PDF files."""
    
    async def parse(self, file_path: str) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            content = await loop.run_in_executor(
                executor,
                self._parse_sync,
                file_path
            )
        return content
    
    def _parse_sync(self, file_path: str) -> Dict[str, Any]:
        text = ""
        metadata = {}
        
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            metadata = {
                "page_count": len(pdf_reader.pages),
                "pdf_metadata": dict(pdf_reader.metadata) if pdf_reader.metadata else {}
            }
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text() or ""
                text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
        
        return {
            "text": text,
            "chunks": self._chunk_text(text),
            "metadata": metadata
        }
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text by pages and then into chunks."""
        pages = text.split("--- Page")
        chunks = []
        
        for page in pages:
            if not page.strip():
                continue
            words = page.split()
            for i in range(0, len(words), CHUNK_SIZE):
                chunk = ' '.join(words[i:i+CHUNK_SIZE])
                if chunk.strip():
                    chunks.append(chunk)
        return chunks
    
    def get_supported_extensions(self) -> List[str]:
        return ['pdf']


class DocxParser(DocumentParser):
    """Parser for DOCX files."""
    
    async def parse(self, file_path: str) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            content = await loop.run_in_executor(
                executor,
                self._parse_sync,
                file_path
            )
        return content
    
    def _parse_sync(self, file_path: str) -> Dict[str, Any]:
        doc = DocxDocument(file_path)
        paragraphs = []
        
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text)
        
        text = "\n\n".join(paragraphs)
        
        # Simple metadata without complex properties
        metadata = {
            "paragraph_count": len(paragraphs),
            "word_count": len(text.split()),
            "character_count": len(text),
        }
        metadata["filename"] = os.path.basename(file_path)
        
        return {
            "text": text,
            "chunks": self._chunk_text(text),
            "metadata": metadata
        }
    
    def _chunk_text(self, text: str) -> List[str]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), CHUNK_SIZE):
            chunk = ' '.join(words[i:i+CHUNK_SIZE])
            chunks.append(chunk)
        return chunks
    
    def get_supported_extensions(self) -> List[str]:
        return ['docx']


class ImageParser(DocumentParser):
    """Parser for images using OCR."""
    
    async def parse(self, file_path: str) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            content = await loop.run_in_executor(
                executor,
                self._parse_sync,
                file_path
            )
        return content
    
    def _parse_sync(self, file_path: str) -> Dict[str, Any]:
        # Open image
        image = Image.open(file_path)
        
        # Perform OCR
        text = pytesseract.image_to_string(image)
        
        return {
            "text": text,
            "chunks": self._chunk_text(text),
            "metadata": {
                "image_size": image.size,
                "image_format": image.format,
                "image_mode": image.mode
            }
        }
    
    def _chunk_text(self, text: str) -> List[str]:
        sentences = re.split(r'(?<=[.!?]) +', text)
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            if current_size + sentence_words > CHUNK_SIZE and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_size = sentence_words
            else:
                current_chunk.append(sentence)
                current_size += sentence_words
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def get_supported_extensions(self) -> List[str]:
        return ['jpg', 'jpeg', 'png']


class ParserFactory:
    """Factory to get appropriate parser for file type."""
    
    def __init__(self):
        self.parsers = [
            PDFParser(),
            DocxParser(),
            TextParser(),
            ImageParser()
        ]
        self.parser_map = {}
        for parser in self.parsers:
            for ext in parser.get_supported_extensions():
                self.parser_map[ext] = parser
    
    def get_parser(self, file_extension: str) -> Optional[DocumentParser]:
        """Get parser for file extension."""
        return self.parser_map.get(file_extension.lower())