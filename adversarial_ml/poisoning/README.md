# Envenenamiento de Datos (Data Poisoning) y Ataques de Backdoor

Los ataques de envenenamiento de datos corrompen el proceso de entrenamiento de un modelo de aprendizaje automático introduciendo muestras maliciosas en el conjunto de datos de entrenamiento. Un tipo específico y popular son los ataques de backdoor.

**Características:**

*   **Objetivo:**
    *   **Envenenamiento General:** Degradar el rendimiento general del modelo.
    *   **Ataques de Backdoor (Puerta Trasera):** Hacer que el modelo se comporte de manera incorrecta para entradas específicas (activadas por un "trigger" o disparador) mientras funciona normalmente para otras entradas.
*   **Impacto:** Denegación de servicio (reduciendo la precisión del modelo), control del comportamiento del modelo para ciertas entradas, compromiso de la integridad del modelo.
*   **Desafío:** Los datos envenenados pueden ser difíciles de detectar si están bien diseñados.

**Herramientas Relevantes:**

*   [Adversarial Robustness Toolbox (ART)](https://github.com/Trusted-AI/adversarial-robustness-toolbox) - Incluye implementaciones de ataques de envenenamiento.
*   [BackdoorBox](https://github.com/THUYimingLi/BackdoorBox)
*   [BadNets (Concepto y Paper)](https://arxiv.org/abs/1708.06733)

**Papers Fundamentales:**

*   [Poisoning Attacks against Support Vector Machines](https://arxiv.org/abs/1206.6389)
*   [BadNets: Identifying Vulnerabilities in the Machine Learning Model Supply Chain](https://arxiv.org/abs/1708.06733)
*   [Targeted Backdoor Attacks on Deep Learning Systems Using Data Poisoning](https://arxiv.org/abs/1712.05526)
*   [Neural Cleanse: Identifying and Mitigating Backdoor Attacks in Neural Networks](https://ieeexplore.ieee.org/document/8835365)
