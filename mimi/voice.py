
import subprocess


class MimiVoice:
    def __init__(self):
        pass

    def speak(self, text):
        if not text or not text.strip():
            return

        print("VOICE DEBUG: Starting Windows speech...")

        script = """
        $text = [Console]::In.ReadToEnd()
        Add-Type -AssemblyName System.Speech
        $speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
        $voice = $speaker.GetInstalledVoices() |
            Where-Object { $_.VoiceInfo.Name -like '*Zira*' } |
            Select-Object -First 1

        if ($voice) {
            $speaker.SelectVoice($voice.VoiceInfo.Name)
        }

        $speaker.Rate = 1
        $speaker.Speak($text)
        $speaker.Dispose()
        """

        subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            input=str(text),
            text=True,
            check=True
        )

        print("VOICE DEBUG: Speech completed!")


