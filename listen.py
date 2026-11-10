
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from pathlib import Path
import json
from scipy.signal import resample_poly

class MimiListener:

    def __init__(self):
        self.sample_rate = 16000
        self.recording_rate = 44100
        model_path = Path(__file__).parent.parent / "vosk-model-en-us-0.22-lgraph"

        print("MIMI: Loading speech recognition...")
        self.model = Model(str(model_path))

    def listen(self, duration=8):
        print("MIMI: I'm listening...")

        audio = sd.rec(
            int(duration * self.recording_rate),
            samplerate=self.recording_rate,
            channels=1,
            dtype="int16",
            device=1
        )

        sd.wait()

        audio = resample_poly(audio, 160, 441).astype("int16")

        recognizer = KaldiRecognizer(
            self.model,
            self.sample_rate
        )

        recognizer.AcceptWaveform(audio.tobytes())

        result = json.loads(recognizer.FinalResult())

        text = result.get("text", "").strip()

        print("MIMI heard:", text)

        return text
