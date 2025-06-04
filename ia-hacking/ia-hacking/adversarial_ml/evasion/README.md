# Evasión de Modelos (Ejemplos Adversarios) con FGSM en MNIST

Esta sección contiene una implementación del ataque **Fast Gradient Sign Method (FGSM)** para generar ejemplos adversarios en el conjunto de datos MNIST. El objetivo es tomar una imagen que un modelo de red neuronal convolucional (CNN) clasifica correctamente, y modificarla ligeramente de tal manera que el modelo la clasifique incorrectamente, mientras que para un humano la imagen sigue pareciendo la original.

## Archivos

*   : Script principal que realiza lo siguiente:
    1.  Define una arquitectura CNN simple.
    2.  Carga el conjunto de datos MNIST (en un subdirectorio  local al script).
    3.  Entrena el modelo CNN si no existe un archivo de pesos pre-entrenado ( local al script), o carga los pesos si existe.
    4.  Implementa la función .
    5.  Itera sobre diferentes valores de épsilon (magnitud de la perturbación).
    6.  Para cada épsilon, genera ejemplos adversarios a partir de un subconjunto del conjunto de test.
    7.  Evalúa cómo cambian las predicciones del modelo en los ejemplos adversarios.
    8.  Guarda una imagen ( local al script) mostrando algunos ejemplos de imágenes originales, sus predicciones, las imágenes adversarias y las nuevas predicciones.
*    (se genera después de la primera ejecución, local al script): Pesos del modelo CNN entrenado en MNIST.
*    (se genera después de la primera ejecución, local al script): Visualización de ejemplos adversarios.
*    (se crea en la primera ejecución): Contiene el dataset MNIST descargado.

## Conceptos Clave

### Fast Gradient Sign Method (FGSM)

Propuesto por Goodfellow et al. en "[Explaining and Harnessing Adversarial Examples](https://arxiv.org/abs/1412.6572)", FGSM es un ataque de caja blanca (requiere acceso a los gradientes del modelo). La idea es realizar una perturbación en la dirección del signo del gradiente de la función de pérdida con respecto a la entrada.

La fórmula es:
`x' = x + epsilon * sign(nabla_x J(theta, x, y))`
Donde:
*   `x'` es la imagen adversaria.
*   `x` es la imagen original.
*   `epsilon` es un multiplicador pequeño para asegurar que la perturbación sea pequeña.
*   `nabla_x J(theta, x, y)` es el gradiente de la función de pérdida `J` con respecto a la imagen de entrada `x`.
*   `sign(...)` extrae el signo de cada elemento del gradiente.
*   `y` es la etiqueta verdadera de `x`.

### Épsilon (ε)

Este parámetro controla la magnitud de la perturbación.
*   Un `epsilon` más alto generalmente resulta en una mayor tasa de éxito del ataque (más imágenes mal clasificadas) pero también hace que la perturbación sea más visible.
*   Un `epsilon` igual a 0 significa que no hay perturbación (se muestra la precisión original en imágenes bien clasificadas).

## Cómo Ejecutar

1.  **Asegúrate de tener las dependencias instaladas.**
    Necesitarás PyTorch, Torchvision y Matplotlib. Puedes instalarlas desde el  del repositorio principal (asegúrate de descomentar , ,  y  si están comentados y no los tienes ya).
    `pip install torch torchvision matplotlib numpy`
    (Si tienes GPU y quieres usarla, instala la versión de PyTorch con soporte CUDA).

2.  **Navega al directorio del script y ejecútalo:**
    `cd ia-hacking/adversarial_ml/evasion/`
    `python fgsm_mnist_attack.py`

    La primera vez que se ejecute, el script:
    *   Descargará el dataset MNIST en .
    *   Entrenará el modelo CNN simple y guardará los pesos en .
    *   Luego procederá con los ataques y generará la imagen .

    En ejecuciones posteriores, cargará los pesos del modelo pre-entrenado directamente.

## Resultados Esperados

*   Verás en la consola información sobre el proceso de entrenamiento (si es la primera vez), y luego los resultados del ataque para diferentes valores de épsilon.
*   Se generará una imagen  en el directorio  mostrando algunos ejemplos de cómo las imágenes son perturbadas y cómo cambian las predicciones del modelo.

Este ejemplo sirve como una introducción práctica a los ataques de evasión y cómo se pueden implementar.
