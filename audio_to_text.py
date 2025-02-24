import whisper
import os

model = whisper.load_model("turbo")

directory = "interviews/"

for filename in os.listdir(directory):
    if filename.endswith(".mp3"):
        file_path = os.path.join(directory, filename)
        print(f"Transcription de {filename} en cours...")

        result = model.transcribe(file_path)
        
        output_filename = os.path.splitext(filename)[0] + ".txt"
        output_path = os.path.join(directory, output_filename)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result["text"])
        
        print(f"Transcription de {filename} terminée et enregistrée dans {output_filename}")