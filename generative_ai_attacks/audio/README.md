# Ataques con Audio Generativo (Deepfake Audio)

La IA generativa permite crear o clonar voces humanas con un realismo sorprendente, lo que se conoce como "deepfake audio".

**Usos Ofensivos:**

*   **Vishing (Voice Phishing):** Suplantar la voz de una persona de confianza (ej. un CEO, un familiar) para solicitar transferencias de dinero, información sensible o credenciales.
*   **Desinformación:** Crear grabaciones falsas de figuras públicas diciendo cosas que nunca dijeron.
*   **Manipulación y Acoso:** Generar audio falso para incriminar o acosar a individuos.
*   **Contraseñas de Voz:** Potencialmente, para burlar sistemas de autenticación basados en voz (aunque muchos sistemas tienen defensas contra la reproducción).

**Herramientas de Generación (Ejemplos):**

*   [Real-Time-Voice-Cloning (CorentinJ)](https://github.com/CorentinJ/Real-Time-Voice-Cloning)
*   [Lyrebird (ahora parte de Descript)](https://www.descript.com/lyrebird-ai) (Comercial, pero pionera)
*   [Vall-E-X (Plachtaa)](https://github.com/Plachtaa/VALL-E-X): Implementación de VALL-E de Microsoft.
*   [OpenVoice (myshell-ai)](https://github.com/myshell-ai/OpenVoice)

**Herramientas y Técnicas de Detección:**

*   Análisis de artefactos en el audio.
*   Modelos de ML entrenados para distinguir audio real de sintético. (Ver sección de recursos generales).
*   [ASVspoof Challenge](https://www.asvspoof.org/): Un desafío para el desarrollo de contramedidas contra la suplantación de voz.

**Papers Relevantes:**

*   [Authenticating Audio Recordings: A Survey of Techniques and Challenges](https://arxiv.org/abs/2004.06639)
*   [DeepSonar: Towards Effective and Robust Detection of AI-Synthesized Fake Voices](https://dl.acm.org/doi/abs/10.1145/3394171.3413716)
