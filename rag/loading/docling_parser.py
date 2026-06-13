from docling.document_converter import DocumentConverter


document = DocumentConverter()

# THis method returns a docling object, passing a raw text, then text splitter has to guess where the tables, headings begin and end
def parse_file(file_path: str):
    try:
        result = document.convert(file_path)
        # mark_down_text = result.document.export_to_markdown()
        # return markdown_data
        return result.document
    except:
        raise Exception("Error parsing file")

# if __name__ == "__main__":
#     from pathlib import Path
    
#     # Path(__file__) is this file: rag/loading/docling_parser.py
#     # .parent.parent takes us back to: rag/
#     test_file = Path(__file__).resolve().parent.parent / "data/documents/general/code_of_conduct.pdf"
    
#     print(f"Loading test file: {test_file}")
#     markdown_data = parse_file(str(test_file)).export_to_markdown()
#     print(markdown_data)


