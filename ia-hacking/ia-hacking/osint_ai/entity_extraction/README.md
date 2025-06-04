# Extracción de Entidades Nombradas (NER) para OSINT con NLTK

Este script demuestra cómo utilizar la librería NLTK (Natural Language Toolkit) en Python para realizar Reconocimiento de Entidades Nombradas (NER) en un texto. NER es una tarea de Procesamiento de Lenguaje Natural (NLP) que busca identificar y clasificar menciones de entidades nombradas en texto no estructurado en categorías predefinidas como personas, organizaciones, ubicaciones, fechas, etc.

En el contexto de OSINT (Inteligencia de Fuentes Abiertas), NER es muy útil para procesar grandes volúmenes de texto (artículos de noticias, informes, publicaciones en redes sociales) y extraer rápidamente información clave sobre individuos, empresas involucradas, y lugares mencionados.

## Archivos

*   `ner_osint_demo.py`: Script de Python que:
    1.  Incluye una función para intentar descargar los recursos necesarios de NLTK (`punkt` para tokenización, `averaged_perceptron_tagger` para etiquetado PoS, `maxent_ne_chunker` para NER, y `words` corpus) si no se encuentran. Los recursos se intentan descargar en un subdirectorio local `nltk_data` relativo al script.
    2.  Define una función `extract_entities_from_text` que toma un texto y devuelve un diccionario con las entidades encontradas (PERSON, ORGANIZATION, LOCATION).
    3.  Contiene un texto de ejemplo simulando un comunicado de prensa o noticia.
    4.  Procesa el texto de ejemplo y muestra las entidades extraídas.
*   `nltk_data/` (directorio, se crea si es necesario por el script): Donde se descargarán los paquetes de NLTK para uso local del script.

## Dependencias

*   **NLTK:** La librería principal de NLP utilizada. Necesitarás instalarla:
    \`\`\`bash
    pip install nltk
    \`\`\`
    El script intentará descargar los paquetes adicionales de NLTK (`punkt`, `averaged_perceptron_tagger`, `maxent_ne_chunker`, `words`) automáticamente en el subdirectorio `nltk_data` dentro de `ia-hacking/osint_ai/entity_extraction/`. Si esto falla debido a restricciones de red o permisos, puede que necesites descargarlos manualmente. Puedes hacerlo ejecutando Python, e importando nltk, luego `nltk.download("punkt", download_dir="./nltk_data")` (y similar para los otros paquetes), asegurándote de ejecutar esto desde el directorio `ia-hacking/osint_ai/entity_extraction/` o ajustando la ruta.

## Cómo Ejecutar

1.  Asegúrate de tener Python y pip instalados.
2.  Instala NLTK: `pip install nltk`
3.  Navega al directorio del script:
    \`\`\`bash
    cd ia-hacking/osint_ai/entity_extraction/
    python ner_osint_demo.py
    \`\`\`
    La primera vez, podría tomar un momento si necesita descargar los paquetes de NLTK. El script los guardará en `ia-hacking/osint_ai/entity_extraction/nltk_data/`.

## Resultados Esperados

El script imprimirá:
*   Mensajes sobre la verificación y descarga de recursos de NLTK (si es necesario).
*   El texto de ejemplo que se está analizando.
*   Una lista de las entidades PERSON (personas), ORGANIZATION (organizaciones) y LOCATION (ubicaciones/GPEs) encontradas en el texto.

## Notas

*   El reconocedor de entidades de NLTK es bueno para empezar, pero modelos más avanzados (como los basados en Transformers, ej. spaCy o Hugging Face) pueden ofrecer mayor precisión y reconocer más tipos de entidades, aunque suelen requerir la descarga de modelos más grandes y pueden tener otras dependencias.
*   La calidad de la extracción de entidades depende mucho de la calidad y el tipo de texto de entrada, así como de la robustez de los modelos de NLTK subyacentes.
