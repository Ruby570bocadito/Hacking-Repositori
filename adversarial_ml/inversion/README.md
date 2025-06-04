# Inversión de Modelos (Model Inversion) / Inferencia de Atributos

La inversión de modelos y la inferencia de atributos son ataques que buscan extraer información sensible sobre los datos de entrenamiento originales o las características que el modelo ha aprendido.

**Características:**

*   **Objetivo:**
    *   **Inversión de Modelo:** Reconstruir muestras de datos de entrenamiento o partes de ellas.
    *   **Inferencia de Pertenencia (Membership Inference):** Determinar si una muestra de datos específica fue utilizada durante el entrenamiento del modelo.
    *   **Inferencia de Propiedad (Property Inference):** Deducir propiedades estadísticas de los datos de entrenamiento que no fueron explícitamente codificadas como características.
*   **Impacto:** Violación de la privacidad de los datos, revelación de información sensible utilizada para entrenar el modelo.

**Herramientas Relevantes:**

*   [Adversarial Robustness Toolbox (ART)](https://github.com/Trusted-AI/adversarial-robustness-toolbox) - Incluye implementaciones de ataques de inferencia.
*   [ML-Leaks](https://github.com/AhmedSalem2/ML-Leaks) (No directamente una herramienta, pero un benchmark y estudio importante)

**Papers Fundamentales:**

*   [Model Inversion Attacks that Exploit Confidence Information and Basic Countermeasures](https://dl.acm.org/doi/10.1145/2810103.2813677)
*   [Membership Inference Attacks Against Machine Learning Models](https://arxiv.org/abs/1610.05820)
*   [The Secret Sharer: Evaluating and Testing Unintended Memorization in Neural Networks](https://arxiv.org/abs/1802.08232)
*   [Extracting Training Data from Large Language Models](https://arxiv.org/abs/2012.07805)
