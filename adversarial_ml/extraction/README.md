# Extracción de Modelos (Model Extraction)

La extracción de modelos es un tipo de ataque de Adversarial Machine Learning donde el objetivo del adversario es robar o replicar un modelo de aprendizaje automático al que tienen acceso limitado (por ejemplo, a través de una API).

**Características:**

*   **Objetivo:** Crear una copia funcional (un modelo sustituto) del modelo objetivo.
*   **Acceso:** Generalmente se asume acceso de caja negra (black-box), donde el atacante solo puede hacer consultas al modelo y observar las salidas. En algunos casos, puede ser de caja gris (gray-box).
*   **Métodos Comunes:** Implican consultar el modelo objetivo con un conjunto de datos (a veces sintético) y usar las predicciones para entrenar un nuevo modelo.
*   **Impacto:** Robo de propiedad intelectual, posibilidad de descubrir vulnerabilidades en el modelo robado, o usarlo para ataques de evasión más efectivos.

**Herramientas Relevantes:**

*   [Adversarial Robustness Toolbox (ART)](https://github.com/Trusted-AI/adversarial-robustness-toolbox) - Incluye implementaciones de ataques de extracción.
*   [Knockoff Nets](https://arxiv.org/abs/1812.02766) (Paper y concepto)

**Papers Fundamentales:**

*   [Stealing Machine Learning Models via Prediction APIs](https://arxiv.org/abs/1609.02943)
*   [Knockoff Nets: Stealing Functionality of Black-Box Models](https://arxiv.org/abs/1812.02766)
*   [High Accuracy and High Fidelity Extraction of Neural Networks](https://arxiv.org/abs/1909.01838)
