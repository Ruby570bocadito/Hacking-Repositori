import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import numpy as np
import matplotlib.pyplot as plt
import os # Importar os para os.path.exists

# Definición de un modelo CNN simple para MNIST
class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.relu3 = nn.ReLU()
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.pool1(self.relu1(self.conv1(x)))
        x = self.pool2(self.relu2(self.conv2(x)))
        x = x.view(-1, 64 * 7 * 7)
        x = self.relu3(self.fc1(x))
        x = self.fc2(x)
        return x

# Función para el ataque FGSM
def fgsm_attack(image, epsilon, data_grad):
    # Recolectar el signo del gradiente
    sign_data_grad = data_grad.sign()
    # Crear la imagen perturbada sumando la pequeña perturbación epsilon * sign_data_grad
    perturbed_image = image + epsilon * sign_data_grad
    # Asegurar que la imagen perturbada esté en el rango [0,1]
    perturbed_image = torch.clamp(perturbed_image, 0, 1)
    return perturbed_image

def train_model_if_not_exists(model, device, train_loader, model_path="mnist_cnn.pth"):
    # Ajustar la ruta del modelo para que esté dentro del directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path_in_script_dir = os.path.join(script_dir, model_path)

    if os.path.exists(model_path_in_script_dir):
        print(f"Cargando modelo pre-entrenado desde {model_path_in_script_dir}")
        model.load_state_dict(torch.load(model_path_in_script_dir, map_location=device))
        model.eval()
        return model
    elif os.path.exists(model_path): # Comprobar si está en el CWD (ej. raíz del proyecto)
        print(f"Cargando modelo pre-entrenado desde {model_path} (CWD)")
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.eval()
        # Opcional: copiar al directorio del script para futuras ejecuciones más directas
        # torch.save(model.state_dict(), model_path_in_script_dir)
        return model


    print(f"Entrenando nuevo modelo y guardándolo en {model_path_in_script_dir}")
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    epochs = 3 # Reducido para rapidez en la demo

    for epoch in range(epochs):
        running_loss = 0.0
        for i, data in enumerate(train_loader, 0):
            inputs, labels = data
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        print(f"Epoch {epoch+1}, Loss: {running_loss/len(train_loader)}")

    print("Entrenamiento finalizado.")
    torch.save(model.state_dict(), model_path_in_script_dir)
    model.eval()
    return model

def test_adversarial_attack(model, device, test_loader, epsilon):
    correct = 0
    adv_examples = []
    processed_count = 0

    for data, target in test_loader:
        data, target = data.to(device), target.to(device)
        data.requires_grad = True

        output = model(data)
        init_pred = output.max(1, keepdim=True)[1]

        if init_pred.item() != target.item():
            processed_count+=1
            # Si ya hemos procesado suficientes y no encontramos ejemplos, parar.
            if processed_count >= len(test_loader) and not adv_examples :
                 print("Todas las predicciones iniciales fueron incorrectas o no se encontraron ejemplos adversarios.")
                 break
            continue

        loss = nn.CrossEntropyLoss()(output, target)
        model.zero_grad()
        loss.backward()
        data_grad = data.grad.data

        perturbed_data = fgsm_attack(data, epsilon, data_grad)
        output_adv = model(perturbed_data)
        final_pred = output_adv.max(1, keepdim=True)[1]

        if final_pred.item() == target.item():
            correct += 1
        else:
            if len(adv_examples) < 5: # Guardar hasta 5 ejemplos
                adv_ex = perturbed_data.squeeze().detach().cpu().numpy()
                orig_ex = data.squeeze().detach().cpu().numpy()
                adv_examples.append((init_pred.item(), final_pred.item(), orig_ex, adv_ex))

        processed_count+=1
        # Detener después de procesar un número limitado de imágenes para la demo si ya tenemos ejemplos
        if len(adv_examples) >= 5 :
            # print(f"Se han recolectado {len(adv_examples)} ejemplos adversarios. Deteniendo para este epsilon.")
            break
        # O si hemos procesado un número razonable de imágenes
        if processed_count >= min(50, len(test_loader)) and len(adv_examples) > 0: # procesar al menos 50 o todo el test_loader si es menor
            # print(f"Procesadas {processed_count} imágenes. Deteniendo para este epsilon.")
            break

    # Evitar división por cero si test_loader es vacío o todas las preds iniciales fueron incorrectas
    # La métrica de precisión aquí es sobre las imágenes que *inicialmente* se clasificaron correctamente Y fueron atacadas.
    # No es una "accuracy" global del modelo en el conjunto de test adversario completo.
    # Es más bien: "De las que acertaba, ¿cuántas sigue acertando DESPUÉS del ataque?"
    # Y el número de ejemplos procesados para esta métrica es el número de imágenes que SÍ fueron atacadas.
    # (aquellas que init_pred.item() == target.item())

    # Contar cuántas imágenes fueron realmente candidatas al ataque
    num_candidates_attacked = 0
    temp_correct_after_attack = 0 # renombramos 'correct' para claridad

    # Re-evaluar para obtener el número de candidatos
    # Esto es ineficiente, pero para la demo y claridad de la métrica:
    # Una mejor forma sería contar los candidatos durante el bucle principal.
    # Aquí, por simplicidad, nos enfocamos en los adv_examples.
    # La 'final_acc' original era confusa.

    # Simplemente reportamos cuántos ejemplos adversarios se crearon con éxito (predicción cambiada)
    successful_adv_examples = 0
    for ex in adv_examples:
        if ex[0] != ex[1]: # init_pred != final_pred
            successful_adv_examples +=1

    if adv_examples: # Si se guardó algún ejemplo (ya sea que haya cambiado la pred o no)
        print(f"Epsilon: {epsilon}\tSe generaron {len(adv_examples)} ejemplos (originalmente correctos). De estos, {successful_adv_examples} cambiaron la predicción.")
    else:
        # Esto puede pasar si epsilon es 0, o si ninguna imagen fue clasificada correctamente al inicio,
        # o si ninguna de las correctamente clasificadas fue afectada por el ataque.
        initial_correct_count = 0
        for data_temp, target_temp in test_loader: # Contar cuántas eran correctas inicialmente
            data_temp, target_temp = data_temp.to(device), target_temp.to(device)
            output_temp = model(data_temp)
            if output_temp.max(1, keepdim=True)[1].item() == target_temp.item():
                initial_correct_count +=1

        if initial_correct_count == 0 and len(test_loader) > 0 :
             print(f"Epsilon: {epsilon}\tNinguna imagen del subconjunto de test fue clasificada correctamente por el modelo base.")
        elif epsilon == 0:
             print(f"Epsilon: {epsilon}\tPrecisión en imágenes limpias (subconjunto): {initial_correct_count}/{len(test_loader)}")
        else:
             print(f"Epsilon: {epsilon}\tNo se generaron ejemplos adversarios exitosos (o no hubo candidatos).")


    return adv_examples

if __name__ == '__main__':
    # Configuración del dispositivo (CPU o GPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Usando dispositivo: {device}")

    # Directorio del script actual
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Crear directorio de datos si no existe, relativo al script
    data_dir = os.path.join(script_dir, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Cargar y transformar el dataset MNIST
    transform = transforms.Compose([
        transforms.ToTensor(),
    ])

    train_dataset = torchvision.datasets.MNIST(root=data_dir, train=True, download=True, transform=transform)
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=64, shuffle=True)

    test_dataset = torchvision.datasets.MNIST(root=data_dir, train=False, download=True, transform=transform)
    subset_indices = list(range(min(100, len(test_dataset)))) # Tomar N imágenes para test rápido
    test_subset = torch.utils.data.Subset(test_dataset, subset_indices)
    test_loader = torch.utils.data.DataLoader(test_subset, batch_size=1, shuffle=False) # No aleatorio para consistencia en ejemplos

    # Inicializar el modelo
    model = SimpleCNN().to(device)
    # El path del modelo ahora se maneja dentro de train_model_if_not_exists
    model = train_model_if_not_exists(model, device, train_loader, model_path="mnist_cnn.pth")

    epsilons = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
    # epsilons = [0, 0.1] # Para pruebas rápidas
    all_adv_examples_collected = []

    for eps in epsilons:
        print(f"\nProbando con Epsilon = {eps}")
        # Pasar una copia del test_loader o re-crearlo si se consume dentro
        # En este caso, test_loader se itera completamente cada vez, está bien.
        adv_ex_for_eps = test_adversarial_attack(model, device, test_loader, eps)
        if eps > 0 and adv_ex_for_eps:
            # Guardar epsilon junto con los ejemplos para referencia en el plot
            for ex_data in adv_ex_for_eps:
                all_adv_examples_collected.append(ex_data + (eps,)) # (init_pred, final_pred, orig_img, adv_img, epsilon)


    if all_adv_examples_collected:
        # Filtrar para mostrar solo ejemplos donde la predicción cambió
        successful_examples_to_plot = [ex for ex in all_adv_examples_collected if ex[0] != ex[1]]

        # Si no hay exitosos, mostrar algunos de los que no cambiaron (si los hay)
        if not successful_examples_to_plot and all_adv_examples_collected:
            print("\nNo se encontraron ejemplos donde la predicción cambió. Mostrando algunos ejemplos perturbados...")
            examples_to_plot = all_adv_examples_collected[:5] # Tomar los primeros 5
        elif not successful_examples_to_plot:
            print("\nNo se recolectaron ejemplos adversarios (ni exitosos ni fallidos).")
            examples_to_plot = []
        else:
            # Intentar obtener una diversidad de epsilons si hay muchos ejemplos exitosos
            # Esto es una heurística simple
            unique_eps_plots = {}
            for ex in successful_examples_to_plot:
                current_eps = ex[4]
                if current_eps not in unique_eps_plots or len(unique_eps_plots[current_eps]) < 1: # 1 ejemplo por epsilon
                    unique_eps_plots.setdefault(current_eps, []).append(ex)

            examples_to_plot = []
            for eps_val in sorted(unique_eps_plots.keys()):
                examples_to_plot.extend(unique_eps_plots[eps_val])

            if len(examples_to_plot) > 5: # Limitar el total de plots
                examples_to_plot = examples_to_plot[:5]
            elif not examples_to_plot and successful_examples_to_plot: # Si la heurística falló, tomar los primeros
                 examples_to_plot = successful_examples_to_plot[:5]


        print(f"\nMostrando hasta {len(examples_to_plot)} ejemplos adversarios...")
        if examples_to_plot:
            num_examples_to_show = len(examples_to_plot)
            plt.figure(figsize=(num_examples_to_show * 4, 4)) # (ancho, alto)

            for i, (init_pred, final_pred, orig_img, adv_img, eps_val) in enumerate(examples_to_plot):
                plt.subplot(2, num_examples_to_show, i + 1)
                plt.xticks([], [])
                plt.yticks([], [])
                plt.imshow(orig_img, cmap="gray")
                plt.title(f"Original\nPred: {init_pred}")

                plt.subplot(2, num_examples_to_show, i + 1 + num_examples_to_show)
                plt.xticks([], [])
                plt.yticks([], [])
                plt.imshow(adv_img, cmap="gray")
                plt.title(f"Adversario (eps={eps_val:.2f})\nPred: {final_pred}")

            plt.tight_layout()
            save_path = os.path.join(script_dir, "fgsm_mnist_examples.png")
            plt.savefig(save_path)
            print(f"Ejemplos adversarios guardados en {save_path}")
        else:
            print("No hay ejemplos adversarios (exitosos o no) para mostrar.")

    else:
        print("No se generaron ejemplos adversarios en ninguna ejecución de épsilon (o el modelo fue 100% robusto).")
    print("Script finalizado.")
