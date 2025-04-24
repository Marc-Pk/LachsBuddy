import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from fastapi import FastAPI, File, UploadFile, Body
from fastapi.responses import FileResponse
import numpy as np
import sounddevice as sd
import tempfile
import uvicorn

app = FastAPI()

class DistilWhisper:
    def __init__(self, model_id="distil-whisper/distil-medium.en"):
        self.device = "cuda:0"# if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id, torch_dtype=self.torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
        )
        self.model.to(self.device)

        self.processor = AutoProcessor.from_pretrained(model_id)

        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            max_new_tokens=128,
            #chunk_length_s=30,
            #batch_size=16,
            torch_dtype=self.torch_dtype,
            device=self.device,
        )
    def __call__(self, audio):
        return self.pipe(audio)["text"]


class SileroTTS:
    def __init__(self):
        self.language = 'en'
        self.speaker = 'v3_en'
        self.device = torch.device('cpu')
        self.silero_tts, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                        model='silero_tts',
                        language=self.language,
                        speaker=self.speaker,
                        device=self.device)

    def __call__(self, phrase):
        return self.silero_tts.apply_tts(text=phrase, sample_rate=24000, speaker="en_3")
            

Silero = SileroTTS()
Whisper = DistilWhisper()

@app.post('/silero_tts/')
async def silero_tts(text: str = Body(...)):
    audio = Silero(text)
    print("Playing audio..." + text)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        temp_audio.write(np.array(audio).tobytes())
        temp_audio.seek(0)
        response = FileResponse(temp_audio.name, media_type="audio/wav")
    
    temp_audio.close()
    return response

@app.post('/distil_whisper/')
async def transcribe_distil_whisper(audio: UploadFile = File(...)):
    audio_file = np.frombuffer(audio.file.read(), dtype=np.int16)
    transcribed_text = Whisper(audio_file)
    print("Transcribed text: " + transcribed_text)
    return transcribed_text

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=5042)