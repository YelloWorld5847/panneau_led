from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Dossier pour stocker les images uploadées
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Route principale
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        content_type = request.form.get("content_type")

        if content_type == "text":
            text = request.form.get("text")
            color = request.form.get("color")
            # Logique pour afficher le texte sur le panneau LED
            print(f"Text to display: {text} with color: {color}")
            # Ajouter ici la commande pour envoyer au panneau LED
        elif content_type == "image":
            if 'image' not in request.files:
                return "No file part", 400
            file = request.files['image']
            if file.filename == '':
                return "No selected file", 400
            if file:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
                # Logique pour afficher l'image sur le panneau LED
                print(f"Image saved at: {filepath}")
                # Ajouter ici la commande pour envoyer l'image au panneau LED
        return redirect(url_for("index"))
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
