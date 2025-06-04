import nltk
import os

# --- Descarga de recursos de NLTK (si es necesario) ---
def download_nltk_resources_if_missing():
    """Intenta descargar recursos de NLTK en un subdirectorio local."""
    resources = {
        "tokenizers/punkt": "punkt",
        "taggers/averaged_perceptron_tagger": "averaged_perceptron_tagger",
        "chunkers/maxent_ne_chunker": "maxent_ne_chunker",
        "corpora/words": "words"
    }
    script_dir = os.path.dirname(__file__)
    download_path = os.path.join(script_dir, "nltk_data")

    if not os.path.exists(download_path):
        print(f"Creando directorio para datos de NLTK: {download_path}")
        os.makedirs(download_path)

    if download_path not in nltk.data.path:
        nltk.data.path.append(download_path)

    all_resources_available = True
    for resource_path, resource_id in resources.items():
        try:
            nltk.data.find(resource_path, paths=[download_path] if os.path.exists(download_path) else None)
            print(f"Recurso {resource_id} encontrado.")
        except nltk.downloader.DownloadError:
            print(f"Recurso {resource_id} no encontrado. Intentando descargar en {download_path}...")
            all_resources_available = False
            try:
                nltk.download(resource_id, download_dir=download_path)
            except Exception as e:
                print(f"ERROR: No se pudo descargar {resource_id}. Detalles: {e}")
                print("Por favor, considera descargar manualmente los recursos de NLTK si el problema persiste.")

    if all_resources_available:
        print("Todos los recursos necesarios de NLTK están disponibles.")
    else:
        print("Advertencia: Algunos recursos de NLTK no pudieron ser descargados o verificados.")
    return all_resources_available

def extract_entities_from_text(text):
    """Extrae PERSON, ORGANIZATION, LOCATION de un texto usando NLTK."""
    entities = {"PERSON": set(), "ORGANIZATION": set(), "LOCATION": set()}
    try:
        sentences = nltk.sent_tokenize(text)
        tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
        tagged_sentences = [nltk.pos_tag(tokens) for tokens in tokenized_sentences]
        chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=False)
    except Exception as e:
        print(f"Error durante el procesamiento NLTK (tokenización/etiquetado/chunking): {e}. ")
        print("Asegúrate de que los paquetes de NLTK (punkt, averaged_perceptron_tagger, maxent_ne_chunker, words) estén correctamente descargados y accesibles.")
        return entities

    for tree in chunked_sentences:
        for subtree in tree.subtrees():
            if hasattr(subtree, "label"):
                entity_label = subtree.label()
                entity_string = " ".join([word for word, tag in subtree.leaves()])
                if entity_label == "PERSON": entities["PERSON"].add(entity_string)
                elif entity_label == "ORGANIZATION": entities["ORGANIZATION"].add(entity_string)
                elif entity_label == "GPE": entities["LOCATION"].add(entity_string) # GPE: Geo-Political Entity
    return entities

if __name__ == "__main__":
    print("--- Demo de Extracción de Entidades para OSINT con NLTK ---")
    print("Intentando verificar y descargar recursos NLTK si es necesario...")
    resources_ok = download_nltk_resources_if_missing()

    if not resources_ok:
        print("ADVERTENCIA: No todos los recursos de NLTK pudieron ser verificados o descargados. La extracción de entidades podría no funcionar correctamente o fallar.")
        print("Por favor, revisa los mensajes de error anteriores. Si la descarga falló, puedes intentar ejecutar el script con acceso a internet o descargar los paquetes manualmente en un intérprete de Python: nltk.download('punkt'), nltk.download('averaged_perceptron_tagger'), etc., en el directorio nltk_data.")

    sample_text_for_osint = ("John Doe, CEO de Acme Corp, anunció hoy en Nueva York una nueva alianza estratégica con Beta Solutions. " + \
                           "El evento tuvo lugar en las oficinas de Beta Solutions en Londres, y contó con la presencia de Jane Smith, la CTO de Beta. " + \
                           "Acme Corp, con sede en San Francisco, espera expandir sus operaciones en Europa. " + \
                           "Google y Microsoft son competidores de Acme Corp.")

    print("\n--- Texto de Ejemplo OSINT ---")
    print(sample_text_for_osint)

    print("\n--- Extrayendo Entidades (NER) ---")
    extracted_entities = extract_entities_from_text(sample_text_for_osint)

    print("\n--- Entidades Encontradas ---")
    if not any(entity_set for entity_set in extracted_entities.values()) and not resources_ok:
        print("No se extrajeron entidades. Esto es esperado si los recursos de NLTK no se pudieron cargar.")
    elif not any(entity_set for entity_set in extracted_entities.values()) and resources_ok:
        print("No se extrajeron entidades del texto de ejemplo, aunque los recursos de NLTK parecen estar listos. Revisa el texto o la lógica de extracción.")
    else:
        for entity_type, entity_set in extracted_entities.items():
            if entity_set: print(f"  {entity_type}: {sorted(list(entity_set))}")
            else: print(f"  {entity_type}: (Ninguna encontrada)")
    print("\n--- Fin de la Demo ---")
