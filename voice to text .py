import tkinter as tk
from tkinter import messagebox
import threading
import speech_recognition as sr
import queue

class VoiceToTextApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice to Text")
        
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        self.is_listening = False
        self.queue = queue.Queue()

        self.toggle_button = tk.Button(root, text="Start Listening", command=self.toggle_listening)
        self.toggle_button.pack(pady=20)
        
        self.text_output = tk.Text(root, height=10, width=50)
        self.text_output.pack(pady=20)

        self.listening_thread = None

        self.update_gui()

    def toggle_listening(self):
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):
        self.is_listening = True
        self.toggle_button.config(text="Stop Listening")
        self.listening_thread = threading.Thread(target=self.listen)
        self.listening_thread.start()

    def listen(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            self.queue.put("Microphone calibrated. Start speaking.\n")
            
            while self.is_listening:
                try:
                    audio = self.recognizer.listen(source, timeout=5)
                    try:
                        text = self.recognizer.recognize_google(audio)
                        self.queue.put(text + '\n')
                    except sr.UnknownValueError:
                        self.queue.put("Google Web Speech API could not understand audio\n")
                    except sr.RequestError as e:
                        self.queue.put(f"Could not request results from Google Web Speech API; {e}\n")
                except sr.WaitTimeoutError:
                    continue

    def stop_listening(self):
        self.is_listening = False
        self.toggle_button.config(text="Start Listening")
        if self.listening_thread is not None:
            self.listening_thread.join()
            self.listening_thread = None
        messagebox.showinfo("Voice to Text", "Stopped listening and displaying the text.")

    def update_gui(self):
        while not self.queue.empty():
            text = self.queue.get_nowait()
            self.text_output.insert(tk.END, text)
            self.text_output.see(tk.END)
        self.root.after(100, self.update_gui)

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceToTextApp(root)
    root.mainloop()
