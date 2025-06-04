# Evasión de Modelos (Model Evasion) / Ejemplos Adversarios

Los ataques de evasión consisten en modificar ligeramente las entradas de un modelo de aprendizaje automático para que este las clasifique incorrectamente en el momento de la inferencia. Estas entradas modificadas se conocen como ejemplos adversarios.

**Características:**

*   **Objetivo:** Engañar al modelo para que produzca una salida incorrecta deseada por el atacante o simplemente una salida incorrecta.
*   **Método:** Se añaden perturbaciones pequeñas (a menudo imperceptibles para los humanos) a las entradas legítimas.
*   **Tipos de Ataque:**
    *   **Caja Blanca (White-box):** El atacante tiene conocimiento completo de la arquitectura y parámetros del modelo.
    *   **Caja Negra (Black-box):** El atacante solo tiene acceso a las predicciones del modelo a través de consultas.
*   **Impacto:** Puede hacer que los sistemas de IA fallen en tareas críticas (ej: clasificación de imágenes, detección de spam, conducción autónoma).

**Herramientas Relevantes:**

*   [Adversarial Robustness Toolbox (ART)](https://github.com/Trusted-AI/adversarial-robustness-toolbox)
*   [Cleverhans](https://github.com/cleverhans-lab/cleverhans)
*   [Foolbox](https://github.com/bethgelab/foolbox)
*   [TextAttack](https://github.com/QData/TextAttack) (para NLP)

**Papers Fundamentales:**

*   [Intriguing properties of neural networks](https://arxiv.org/abs/1312.6199) (Szegedy et al.)
*   [Explaining and Harnessing Adversarial Examples](https://arxiv.org/abs/1412.6572) (Goodfellow et al. - FGSM)
*   [Towards Evaluating the Robustness of Neural Networks](https://arxiv.org/abs/1608.04644) (Carlini & Wagner)
*   [Practical Black-Box Attacks against Machine Learning](https://arxiv.org/abs/1602.02697) (Papernot et al.)
