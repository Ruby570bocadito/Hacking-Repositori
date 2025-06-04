# Ataques con Texto Generativo (LLMs)

Los Modelos de Lenguaje Grandes (LLMs) pueden generar texto coherente y contextualmente relevante, lo que abre la puerta a diversos usos maliciosos.

**Usos Ofensivos:**

*   **Phishing y Spear Phishing:** Generación de correos electrónicos y mensajes altamente personalizados y convincentes.
*   **Desinformación (Fake News):** Creación masiva de artículos de noticias falsas, posts en redes sociales.
*   **Estafas y Fraudes:** Generación de textos para engañar a las víctimas (ej. mensajes de soporte técnico falsos).
*   **Ingeniería Social Automatizada:** Creación de chatbots para interactuar con víctimas a escala.
*   **Generación de Código Malicioso:** Aunque los modelos suelen tener salvaguardas, se investiga su capacidad para ayudar a generar o completar código malicioso.
*   **Ataques de Prompt Injection:** Manipular las instrucciones de un LLM para que realice acciones no deseadas, revele información sensible o genere contenido dañino. Este es un vector de ataque crítico para aplicaciones que integran LLMs.

**Herramientas de Generación (Ejemplos):**

*   **APIs de LLMs Comerciales:**
    *   [OpenAI API (GPT-3, GPT-4)](https://openai.com/api/)
    *   [Google Gemini API](https://ai.google.dev/)
    *   [Anthropic Claude API](https://www.anthropic.com/product)
*   **Modelos de Código Abierto:**
    *   [Llama (Meta)](https://github.com/facebookresearch/llama) y sus variantes.
    *   [Falcon, Mistral, etc.](https://huggingface.co/models) (Disponibles en Hugging Face).
    *   [Ollama](https://github.com/jmorganca/ollama) (Para ejecutar modelos localmente).

**Técnicas de Ataque Específicas para LLMs:**

*   **Prompt Injection:**
    *   **Jailbreaking:** Usar prompts diseñados para eludir las restricciones de seguridad del modelo.
    *   **DAN (Do Anything Now):** Un tipo popular de jailbreak.
    *   **Indirect Prompt Injection:** Cuando un LLM procesa texto de fuentes no confiables (ej. una página web resumida) que contiene instrucciones maliciosas ocultas.
*   **Model Grabbing / Fine-tuning Malicioso:** Intentos de robar la configuración del modelo o influir en su comportamiento mediante fine-tuning con datos maliciosos.

**Herramientas y Recursos para Prompt Injection:**

*   [promptmap](https://github.com/utkusen/promptmap): Escáner de prompt injection.
*   [Rebuff.ai](https://github.com/protectai/rebuff): Detector de prompt injection.
*   [Awesome ChatGPT Prompts (sección de jailbreaks)](https://github.com/f/awesome-chatgpt-prompts)
*   [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) (Ver LLM01: Prompt Injections).

**Detección de Texto Generado por IA:**

*   Es un desafío considerable, ya que los modelos son cada vez mejores.
*   Algunas herramientas intentan detectar patrones, pero pueden tener falsos positivos/negativos.
*   [GPTZero](https://gptzero.me/)
*   [OpenAI AI Text Classifier (Descontinuado, pero conceptualmente relevante)](https://openai.com/blog/new-ai-classifier-for-indicating-ai-written-text/)

**Papers Relevantes:**

*   [Language Models are Few-Shot Learners (GPT-3 Paper)](https://arxiv.org/abs/2005.14165)
*   [Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection](https://arxiv.org/abs/2302.12173)
