from pathlib import Path
from rag.loading.docling_parser import parse_file


ROLE_MAP = {
    "general": ["admin","doctor","nurse","billing_executive","technician"],
    "clinical" : ["admin","doctor"],
    "nursing" : ["admin", "nurse"],
    "billing" : ["admin","billing_executive"],
    "equipment" : ["admin","technician"]

}





def load_documents(base_dir):
    all_documents = []
    # ITerate through all the folders
    for subfolder in base_dir.iterdir():
        if subfolder.is_dir() and subfolder.name in ROLE_MAP.keys():
            # ITerate through all the files in the subfolder
            for file in subfolder.iterdir():
                if file.is_file() and file.suffix.lower() in {'.pdf', '.md'}:
                    docling_obj = parse_file(str(file))
                    collection_name = subfolder.name
                    allowed_roles = ROLE_MAP[collection_name]
                    doc_dict = {
                        "content": docling_obj, 
                        "metadata": {
                            "source_document": file.name,
                            "collection": collection_name,
                            "access_roles": allowed_roles,
                        }
                    }
                    all_documents.append(doc_dict)
                    print(f"Loaded: {file.name} | Collection: {collection_name} | Roles: {allowed_roles}")
            print("-" * 30)
    return all_documents

# base_dir = (Path(__file__).resolve().parents[1] / "data/documents")

# if __name__ == "__main__":
#     load_documents(base_dir)
                    


