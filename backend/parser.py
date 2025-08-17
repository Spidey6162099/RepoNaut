import logging
from tree_sitter import Parser, Language
from tree_sitter_languages import get_language
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# A mapping of language names to their chunking queries.
# The 'language' object is now loaded on-demand inside chunk_file.
LANGUAGES = {
    "python": {
        "queries": [
            "(function_definition) @chunk",
            "(class_definition) @chunk",
        ],
    },
    "javascript": {
        "queries": [
            "(function_declaration) @chunk",
            "(arrow_function) @chunk",
            "(class_declaration) @chunk",
            "(method_definition) @chunk",
        ],
    },
    "java": {
        "queries": [
            "(method_declaration) @chunk",
            "(class_declaration) @chunk",
            "(interface_declaration) @chunk",
        ],
    },
    "cpp": {
        "queries": [
            "(function_definition) @chunk",
            "(class_specifier) @chunk",
            "(struct_specifier) @chunk",
        ],
    },
    "c_sharp": {
        "queries": [
            "(method_declaration) @chunk",
            "(class_declaration) @chunk",
            "(interface_declaration) @chunk",
            "(struct_declaration) @chunk",
        ],
    },
}

def chunk_file(file_content: str, language_name: str) -> List[Dict[str, Any]]:
    """
    Parse the file content and chunk it into a list of dictionaries,
    each representing a function or class.
    """
    if language_name not in LANGUAGES:
        logger.warning(f"No chunking queries defined for language: {language_name}")
        return []

    try:
        # LAZY LOADING: Get the language parser only when it's needed.
        # This resolves the TypeError during test collection.
        language: Language = get_language(language_name)
    except Exception as e:
        logger.error(f"Could not load language parser for '{language_name}': {e}")
        return []

    lang_config = LANGUAGES[language_name]
    parser = Parser()
    parser.set_language(language)

    tree = parser.parse(bytes(file_content, "utf8"))
    root_node = tree.root_node
    
    chunks = []
    
    for query_str in lang_config["queries"]:
        query = language.query(query_str)
        captures = query.captures(root_node)
        
        for node, _ in captures:
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            content = node.text.decode('utf8')
            
            chunks.append({
                "start_line": start_line,
                "end_line": end_line,
                "content": content,
            })
            
    logger.info(f"Chunked {len(chunks)} nodes for language: {language_name}")
    return chunks