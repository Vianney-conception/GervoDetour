from flask import Flask, request, render_template, send_file
from rembg import remove
from PIL import Image
import io

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Suppression du fond des images</title>
    </head>
    <body>
        <h1>Supprimer le fond d'une image</h1>
        <form action="/remove-bg" method="post" enctype="multipart/form-data">
            <input type="file" name="image" accept="image/*" required>
            <button type="submit">Supprimer le fond</button>
        </form>
    </body>
    </html>
    '''

@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    if 'image' not in request.files:
        return "Aucun fichier n'a été envoyé", 400

    file = request.files['image']
    if file.filename == '':
        return "Aucun fichier sélectionné", 400

    try:
        input_image = Image.open(file.stream)
        output_image = remove(input_image)
        output_buffer = io.BytesIO()
        output_image.save(output_buffer, format="PNG")
        output_buffer.seek(0)

        return send_file(output_buffer, mimetype='image/png', as_attachment=True, download_name='image_sans_fond.png')
    except Exception as e:
        return f"Erreur lors du traitement de l'image : {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)