import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import torch
from carvekit.api.high import HiInterface
import threading

class BackgroundRemoverApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Suppression d'Arrière-plan avec CarveKit")
        self.master.geometry("800x650")

        # Statut
        self.status_label = tk.Label(master, text="Chargement de l'interface IA...", fg="blue")
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

        # Chargement de l'IA dans un thread pour ne pas figer l'interface
        threading.Thread(target=self.load_model).start()

    def load_model(self):
        self.set_status("Chargement du modèle CarveKit, cela peut prendre un moment...")
        self.interface = HiInterface(
            object_type="hairs-like",
            batch_size_seg=1,
            batch_size_matting=1,
            device='cuda' if torch.cuda.is_available() else 'cpu',
            seg_mask_size=640,
            matting_mask_size=2048,
            trimap_prob_threshold=231,
            trimap_dilation=30,
            trimap_erosion_iters=5,
            fp16=False
        )
        self.set_status("Modèle chargé. Prêt à traiter les images.")

    def set_status(self, text):
        self.status_label.config(text=text)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.original_image = Image.open(file_path).convert("RGB")
            self.display_image(self.original_image)
            self.process_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.DISABLED)
            self.set_status("Image chargée. Prête à être traitée.")

    def display_image(self, image):
        image_resized = image.resize((400, 400))
        self.tk_image = ImageTk.PhotoImage(image_resized)
        self.image_label.config(image=self.tk_image)

    def start_background_removal(self):
        self.set_status("Traitement en cours... Veuillez patienter.")
        self.process_button.config(state=tk.DISABLED)
        threading.Thread(target=self.remove_background).start()

    def remove_background(self):
        try:
            result = self.interface([self.original_image])
            self.processed_image = result[0]
            self.master.after(0, lambda: self.display_image(self.processed_image))
            self.master.after(0, lambda: self.set_status("Arrière-plan supprimé avec succès."))
            self.master.after(0, lambda: self.save_button.config(state=tk.NORMAL))
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("Erreur", f"Une erreur est survenue : {e}"))
            self.master.after(0, lambda: self.set_status("Erreur lors du traitement."))

    def save_image(self):
        if self.processed_image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG", "*.png")])
            if file_path:
                self.processed_image.save(file_path)
                self.set_status("Image enregistrée avec succès.")
                messagebox.showinfo("Succès", "Image enregistrée avec succès.")

if __name__ == "__main__":
    root = tk.Tk()
    app = BackgroundRemoverApp(root)
    root.mainloop()
