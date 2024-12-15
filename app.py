from flask import Flask, render_template, request, redirect, url_for
import os
import subprocess
import time

app = Flask(__name__)

# Dossier pour stocker les images uploadées
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Variable pour suivre le processus
# current_process = None


STOP_FILE = "/tmp/stop_led_display"

def hex_to_rgb(hex_color):
    """Convertit une couleur hexadécimale en valeurs RGB."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_stop_file():
    """Crée un fichier de contrôle pour stopper tous les programmes LED."""
    if not os.path.exists(STOP_FILE):
        with open(STOP_FILE, "w") as f:
            f.write("STOP")
        print("Fichier de contrôle créé : tous les scripts LED en cours devraient s'arrêter.")
    else:
        print("Le fichier de contrôle existe déjà.")

def remove_stop_file():
    """Supprime le fichier de contrôle pour permettre de redémarrer un script."""
    if os.path.exists(STOP_FILE):
        os.remove(STOP_FILE)
        print("Fichier de contrôle supprimé : les scripts LED peuvent être relancés.")
    else:
        print("Aucun fichier de contrôle trouvé à supprimer.")

def wait_for_scripts_to_stop(timeout=2):
    """
    Attend que les scripts s'arrêtent après la création du fichier de contrôle.
    Utilisez un délai maximum défini par `timeout` (en secondes).
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        print("Attente que les scripts LED s'arrêtent...")
        time.sleep(1)
    print("Les scripts LED devraient être arrêtés maintenant.")


def run_led_command(command):
    # Arrêter les programmes en cours avant d'afficher un nouveau texte
    create_stop_file()
    wait_for_scripts_to_stop()
    remove_stop_file()  # Supprime le fichier de contrôle avant de lancer un nouveau script

    """Exécute une commande pour le panneau LED."""
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())  # Affiche la sortie
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de la commande : {e}")



# Route principale
@app.route("/", methods=["GET", "POST"])
def index():
    content_type = "text"  # Valeur par défaut
    if request.method == "POST":

        action = request.form.get("action")
        print("action = ", action)
        if action == "stop":
            print(1)
            # Si l'action est "stop", on arrête le panneau LED
            # Arrêter les programmes en cours avant d'afficher un nouveau texte
            create_stop_file()
            wait_for_scripts_to_stop(timeout=4)
            remove_stop_file()  # Supprime le fichier de contrôle avant de lancer un nouveau script

            return redirect(url_for("index"))
        else:
            print(2)

        content_type = request.form.get("content_type")

        if content_type == "text":
            text = request.form.get("text")
            hex_color = request.form.get("color")
            print(f"Text to display: {text} with color: {hex_color}")

            # Convertir la couleur hexadécimale en RGB
            red, green, blue = hex_to_rgb(hex_color)

            # Commande pour afficher le texte sur le panneau LED
            # current_process = "~/rpi-rgb-led-matrix/bindings/python/samples/runtext.py"
            command = (
                f"cd ~/rpi-rgb-led-matrix/bindings/python/samples && "
                f"sudo ./runtext.py --led-cols 64 --led-rows 64 -t \"{text}\" "
                f"--red {red} --green {green} --blue {blue}"
            )
            run_led_command(command)
        elif content_type == "image":
            # Vérification si une image a été téléchargée ou sélectionnée depuis la galerie
            selected_image = request.form.get('selected_image')
            if selected_image:
                print(f"Image sent from gallery: {selected_image}")

                # Vérifier si l'image sélectionnée est un fichier GIF
                if selected_image.lower().endswith('.gif'):
                    # Commande spécifique pour afficher un GIF
                    print(f"GIF file detected: {selected_image}")
                    # current_process = "/home/pi/rpi-rgb-led-matrix/utils/led-image-viewer"
                    command = f"cd /home/pi/rpi-rgb-led-matrix/utils && make && sudo ./led-image-viewer {selected_image} --led-cols 64 --led-rows 64"
                else:
                    # current_process = "~/rpi-rgb-led-matrix/bindings/python/samples/image-viewer.py"
                    command = f"cd ~/rpi-rgb-led-matrix/bindings/python/samples && sudo ./image-viewer.py {selected_image} --led-cols 64 --led-rows 64"
                # Commande pour envoyer l'image sélectionnée au panneau LED
                run_led_command(command)
            elif 'image' in request.files:
                file = request.files['image']
                if file.filename:
                    filename = file.filename
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    # Vérifier si le fichier existe déjà dans le dossier
                    if os.path.exists(filepath):
                        print(f"L'image {filename} existe déjà dans le dossier.")
                    else:
                        file.save(filepath)
                        print(f"Image sauvegardée à: {filepath}")

                    # Vérifier si l'image sélectionnée est un fichier GIF
                    if filename.lower().endswith('.gif'):
                        # Commande spécifique pour afficher un GIF
                        print(f"GIF file detected: {filename}")
                        # current_process = "/home/pi/rpi-rgb-led-matrix/utils/led-image-viewer"
                        command = f"cd /home/pi/rpi-rgb-led-matrix/utils && make && sudo ./led-image-viewer {filepath} --led-cols 64 --led-rows 64"
                    else:
                        # current_process = "~/rpi-rgb-led-matrix/bindings/python/samples/image-viewer.py"
                        command = f"cd ~/rpi-rgb-led-matrix/bindings/python/samples && sudo ./image-viewer.py {filepath} --led-cols 64 --led-rows 64"
                    # Commande pour envoyer l'image téléchargée au panneau LED
                    run_led_command(command)


        return redirect(url_for("index"))

    # Gère le cas où une image est sélectionnée depuis la galerie
    selected_image = request.args.get("selected_image")
    if selected_image:
        print(f"Image selected from gallery: {selected_image}")
        # Commande pour envoyer l'image sélectionnée au panneau LED

    return render_template("index.html", content_type=content_type)


# @app.route("/stop_led", methods=["POST"])
# def stop_led():
#     """Arrête le script du panneau LED."""
#     stop_led_display()
#     return redirect(url_for("index"))

@app.route("/gallery")
def gallery():
    # Liste tous les fichiers du dossier UPLOAD_FOLDER
    images = [
        f"static/uploads/{filename}"
        for filename in os.listdir(app.config['UPLOAD_FOLDER'])
        if filename.lower().endswith(('.bmp', '.dib', '.gif', '.im', '.jpeg', '.jpg', '.jp2', '.pcx', '.png', '.ppm', '.tiff', '.webp', '.heif', '.heic'))
    ]

    # Si une image doit être supprimée
    if request.method == "POST":
        image_to_delete = request.form.get("image_to_delete")
        if image_to_delete and os.path.exists(image_to_delete):
            os.remove(image_to_delete)
            print(f"Image supprimée: {image_to_delete}")
            return redirect(url_for("manage_gallery"))

    return render_template("gallery.html", images=images)


# Route pour afficher la galerie d'images avec possibilité de suppression
# @app.route("/manage_gallery", methods=["GET", "POST"])
# def manage_gallery():
#     images = [
#         os.path.join(UPLOAD_FOLDER, filename)
#         for filename in os.listdir(app.config['UPLOAD_FOLDER'])
#         if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
#     ]
#
#     # Si une image doit être supprimée
#     if request.method == "POST":
#         image_to_delete = request.form.get("image_to_delete")
#         if image_to_delete and os.path.exists(image_to_delete):
#             os.remove(image_to_delete)
#             print(f"Image supprimée: {image_to_delete}")
#             return redirect(url_for("manage_gallery"))
#
#     return render_template("manage_gallery.html", images=images)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
