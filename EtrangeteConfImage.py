import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from rembg import remove
import threading
import io

class BackgroundRemoverRembgApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Préparation des images pour l'Etrangete")
        self.master.geometry("800x650")

        self.status_label = tk.Label(master, text="Chargement de GervoDetour prêt à démarrer...", fg="blue")
        self.status_label.pack(pady=5)

        self.image_label = tk.Label(master)
        self.image_label.pack(pady=10)

        self.load_button = tk.Button(master, text="Charger une image", command=self.load_image)
        self.load_button.pack(pady=10)

        self.process_button = tk.Button(master, text="Supprimer l'arrière-plan", command=self.start_background_removal, state=tk.DISABLED)
        self.process_button.pack(pady=10)

        self.save_button = tk.Button(master, text="Enregistrer l'image", command=self.save_image, state=tk.DISABLED)
        self.save_button.pack(pady=10)

        self.original_image = None
        self.processed_image = None

    def set_status(self, text):
        self.status_label.config(text=text)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.original_image = Image.open(file_path).convert("RGBA")
            self.display_image(self.original_image)
            self.process_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.DISABLED)
            self.set_status("Image chargée. Cliquez pour traiter.")

    def display_image(self, image):
        image_resized = image.resize((400, 400))
        self.tk_image = ImageTk.PhotoImage(image_resized)
        self.image_label.config(image=self.tk_image)

    def start_background_removal(self):
        self.set_status("Traitement de l'image en cours...")
        self.process_button.config(state=tk.DISABLED)
        threading.Thread(target=self.remove_background).start()

    def remove_background(self):
        try:
            # Convert image to bytes for rembg
            img_byte_arr = io.BytesIO()
            self.original_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            result_data = remove(img_byte_arr)

            self.processed_image = Image.open(io.BytesIO(result_data)).convert("RGBA")

            self.master.after(0, lambda: self.display_image(self.processed_image))
            self.master.after(0, lambda: self.set_status("Arrière-plan supprimé avec succès."))
            self.master.after(0, lambda: self.save_button.config(state=tk.NORMAL))
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("Erreur", str(e)))
            self.master.after(0, lambda: self.set_status("Erreur pendant le traitement."))

    def save_image(self):
        if self.processed_image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
            if file_path:
                self.processed_image.save(file_path)
                self.set_status("Image enregistrée avec succès.")
                messagebox.showinfo("Succès", "Image enregistrée avec succès.")

if __name__ == "__main__":
    root = tk.Tk()
    app = BackgroundRemoverRembgApp(root)
    root.mainloop()
