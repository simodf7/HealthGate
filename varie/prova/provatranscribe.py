import whisper

model = whisper.load_model("base")
result = model.transcribe("prove_audio/rumore_rita.mp3")
print(result["text"])