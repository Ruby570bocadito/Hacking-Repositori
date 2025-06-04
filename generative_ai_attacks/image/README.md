# Ataques con Imágenes Generativas (Deepfake Images / Synthetic Images)

La IA puede generar imágenes fotorrealistas de personas, objetos o escenas que nunca existieron, o modificar imágenes existentes de manera convincente.

**Usos Ofensivos:**

*   **Creación de Perfiles Falsos:** Generación de fotos de perfil para cuentas falsas en redes sociales, usadas para estafas, desinformación o espionaje.
*   **Desinformación y Propaganda:** Creación de imágenes falsas para manipular la opinión pública o desacreditar a personas.
*   **Robo de Identidad / Suplantación:** Aunque más complejo, se podrían usar para intentar engañar sistemas de reconocimiento facial poco robustos.
*   **Generación de Contenido Ilegal o Dañino:** Creación de imágenes para fines ilícitos.

**Herramientas de Generación (Ejemplos):**

*   **GANs (Generative Adversarial Networks):**
    *   [StyleGAN (NVlabs)](https://github.com/NVlabs/stylegan) y sus variantes (StyleGAN2, StyleGAN3).
    *   [This Person Does Not Exist](https://thispersondoesnotexist.com/) (Demostración popular de StyleGAN).
*   **Modelos de Difusión:**
    *   [Stable Diffusion (Stability AI)](https://github.com/Stability-AI/stablediffusion)
    *   [DALL-E 2 / 3 (OpenAI)](https://openai.com/dall-e-3) (Comercial)
    *   [Midjourney](https://www.midjourney.com/) (Comercial)

**Herramientas y Técnicas de Detección:**

*   Análisis de inconsistencias visuales, artefactos de generación.
*   Modelos de ML entrenados para clasificar imágenes reales vs. sintéticas.
*   [FaceForensics++](https://github.com/ondyari/FaceForensics) (Dataset y benchmarks para detección de deepfakes).

**Papers Relevantes:**

*   [A Style-Based Generator Architecture for Generative Adversarial Networks](https://arxiv.org/abs/1812.04948) (StyleGAN)
*   [Detecting and Characterizing Generalization in Generative Models](https://arxiv.org/abs/1802.06070)
