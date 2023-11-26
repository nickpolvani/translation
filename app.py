import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from audio_processor import AudioProcessor  # Assuming your class is in audio_processor.py
import matplotlib.pyplot as plt

class AudioApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Audio Visualization and Translation")
        self.geometry("800x600")
        self.fig, self.ax = plt.subplots()
        self.audio_processor = AudioProcessor(self.fig, self.ax, update_ui_callback=self.update_ui)

        # Spectrogram Plot
        self.canvas = FigureCanvasTkAgg(self.audio_processor.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Translated Text Display
        self.translated_text = tk.StringVar()
        self.translated_text_label = tk.Label(self, textvariable=self.translated_text, wraplength=400)
        self.translated_text_label.pack(side=tk.BOTTOM)

        # Start and Stop Buttons
        self.start_button = tk.Button(self, text="Start", command=self.start_processing)
        self.start_button.pack(side=tk.LEFT)
        self.stop_button = tk.Button(self, text="Stop", command=self.stop_processing)
        self.stop_button.pack(side=tk.RIGHT)

    def start_processing(self):
        self.audio_processor.run()

    def stop_processing(self):
        self.audio_processor.cleanup()

    def update_ui(self, translated_text):
        self.translated_text.set(translated_text)
        self.canvas.draw()

if __name__ == "__main__":
    app = AudioApp()
    app.mainloop()
