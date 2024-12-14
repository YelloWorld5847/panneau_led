from flask import Flask, render_template, request, redirect, url_for
import os
import subprocess

app = Flask(__name__)

# Dossier pour stocker les images uploadées
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def run_led_command(command):
    """Exécute une commande pour le panneau LED."""
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())  # Affiche la sortie
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de la commande : {e.stderr.decode()}")

# Route principale
@app.route("/", methods=["GET", "POST"])
def index():
    content_type = "text"  # Valeur par défaut
    if request.method == "POST":
        content_type = request.form.get("content_type")

        if content_type == "text":
            text = request.form.get("text")
            color = request.form.get("color")
            print(f"Text to display: {text} with color: {color}")
            # Commande pour afficher le texte sur le panneau LED
            command = f"cd ~/rpi-rgb-led-matrix/bindings/python/samples && sudo ./runtext.py --led-cols 64 --led-rows 64 -t \"{text}\""
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
                    command = f"cd /home/pi/rpi-rgb-led-matrix/utils && make && sudo ./led-image-viewer {selected_image} --led-cols 64 --led-rows 64"
                else:
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
                        command = f"cd /home/pi/rpi-rgb-led-matrix/utils && make && sudo ./led-image-viewer {filepath} --led-cols 64 --led-rows 64"
                    else:
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


@app.route("/gallery")
def gallery():
    # Liste tous les fichiers du dossier UPLOAD_FOLDER
    images = [
        f"static/uploads/{filename}"
        for filename in os.listdir(app.config['UPLOAD_FOLDER'])
        # if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', ''))
    ]
    return render_template("gallery.html", images=images)




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
