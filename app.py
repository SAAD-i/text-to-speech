from flask import Flask, request, jsonify, render_template
from TTS.api import TTS
import os
import fitz  # PyMuPDF
import docx
from io import BytesIO
import base64

app = Flask(__name__)

# Available TTS and vocoder models
tts_models = {
    "Multilingual xTTS v2": "tts_models/multilingual/multi-dataset/xtts_v2",
    "Multilingual xTTS v1.1": "tts_models/multilingual/multi-dataset/xtts_v1.1",
    "Multilingual YourTTS": "tts_models/multilingual/multi-dataset/your_tts",
    "Multilingual Bark": "tts_models/multilingual/multi-dataset/bark",
    "Bulgarian VITS": "tts_models/bg/cv/vits",
    "Czech VITS": "tts_models/cs/cv/vits",
    "Danish VITS": "tts_models/da/cv/vits",
    "Estonian VITS": "tts_models/et/cv/vits",
    "Irish VITS": "tts_models/ga/cv/vits",
    "English EK1 Tacotron2": "tts_models/en/ek1/tacotron2",
    "English LJSpeech Tacotron2-DDC": "tts_models/en/ljspeech/tacotron2-DDC",
    "English LJSpeech Tacotron2-DDC_ph": "tts_models/en/ljspeech/tacotron2-DDC_ph",
    "English LJSpeech Glow-TTS": "tts_models/en/ljspeech/glow-tts",
    "English LJSpeech Speedy-Speech": "tts_models/en/ljspeech/speedy-speech",
    "English LJSpeech Tacotron2-DCA": "tts_models/en/ljspeech/tacotron2-DCA",
    "English LJSpeech VITS": "tts_models/en/ljspeech/vits",
    "English LJSpeech VITS Neon": "tts_models/en/ljspeech/vits--neon",
    "English LJSpeech FastPitch": "tts_models/en/ljspeech/fast_pitch",
    "English LJSpeech Overflow": "tts_models/en/ljspeech/overflow",
    "English LJSpeech Neural HMM": "tts_models/en/ljspeech/neural_hmm",
    "English VCTK VITS": "tts_models/en/vctk/vits",
    "English VCTK FastPitch": "tts_models/en/vctk/fast_pitch",
    "English SAM Tacotron-DDC": "tts_models/en/sam/tacotron-DDC",
    "English Blizzard2013 Capacitron-T2-C50": "tts_models/en/blizzard2013/capacitron-t2-c50",
    "English Blizzard2013 Capacitron-T2-C150_v2": "tts_models/en/blizzard2013/capacitron-t2-c150_v2",
    "English Multi-Dataset Tortoise-v2": "tts_models/en/multi-dataset/tortoise-v2",
    "English Jenny": "tts_models/en/jenny/jenny",
    "Spanish MAI Tacotron2-DDC": "tts_models/es/mai/tacotron2-DDC",
    "Spanish CSS10 VITS": "tts_models/es/css10/vits",
    "French MAI Tacotron2-DDC": "tts_models/fr/mai/tacotron2-DDC",
    "French CSS10 VITS": "tts_models/fr/css10/vits",
    "Ukrainian MAI Glow-TTS": "tts_models/uk/mai/glow-tts",
    "Ukrainian MAI VITS": "tts_models/uk/mai/vits",
    "Chinese Baker Tacotron2-DDC-GST": "tts_models/zh-CN/baker/tacotron2-DDC-GST",
    "Dutch MAI Tacotron2-DDC": "tts_models/nl/mai/tacotron2-DDC",
    "Dutch CSS10 VITS": "tts_models/nl/css10/vits",
    "German Thorsten Tacotron2-DCA": "tts_models/de/thorsten/tacotron2-DCA",
    "German Thorsten VITS": "tts_models/de/thorsten/vits",
    "German Thorsten Tacotron2-DDC": "tts_models/de/thorsten/tacotron2-DDC",
    "German CSS10 VITS Neon": "tts_models/de/css10/vits-neon",
    "Japanese Kokoro Tacotron2-DDC": "tts_models/ja/kokoro/tacotron2-DDC",
    "Turkish Common Voice Glow-TTS": "tts_models/tr/common-voice/glow-tts",
    "Italian Female Glow-TTS": "tts_models/it/mai_female/glow-tts",
    "Italian Female VITS": "tts_models/it/mai_female/vits",
    "Italian Male Glow-TTS": "tts_models/it/mai_male/glow-tts",
    "Italian Male VITS": "tts_models/it/mai_male/vits",
    "Ewe OpenBible VITS": "tts_models/ewe/openbible/vits",
    "Hausa OpenBible VITS": "tts_models/hau/openbible/vits",
    "Lingala OpenBible VITS": "tts_models/lin/openbible/vits",
    "Twi Akuapem OpenBible VITS": "tts_models/tw_akuapem/openbible/vits",
    "Twi Asante OpenBible VITS": "tts_models/tw_asante/openbible/vits",
    "Yoruba OpenBible VITS": "tts_models/yor/openbible/vits",
    "Hungarian CSS10 VITS": "tts_models/hu/css10/vits",
    "Greek Common Voice VITS": "tts_models/el/cv/vits",
    "Finnish CSS10 VITS": "tts_models/fi/css10/vits",
    "Croatian Common Voice VITS": "tts_models/hr/cv/vits",
    "Lithuanian Common Voice VITS": "tts_models/lt/cv/vits",
    "Latvian Common Voice VITS": "tts_models/lv/cv/vits",
    "Maltese Common Voice VITS": "tts_models/mt/cv/vits",
    "Polish Female VITS": "tts_models/pl/mai_female/vits",
    "Portuguese Common Voice VITS": "tts_models/pt/cv/vits",
    "Romanian Common Voice VITS": "tts_models/ro/cv/vits",
    "Slovak Common Voice VITS": "tts_models/sk/cv/vits",
    "Slovenian Common Voice VITS": "tts_models/sl/cv/vits",
    "Swedish Common Voice VITS": "tts_models/sv/cv/vits",
    "Catalan Custom VITS": "tts_models/ca/custom/vits",
    "Persian Custom Glow-TTS": "tts_models/fa/custom/glow-tts",
    "Bengali Custom VITS Male": "tts_models/bn/custom/vits-male",
    "Bengali Custom VITS Female": "tts_models/bn/custom/vits-female",
    "Belarusian Common Voice Glow-TTS": "tts_models/be/common-voice/glow-tts",
}

vocoder_models = {
    "Universal Libri-TTS WaveGrad": "vocoder_models/universal/libri-tts/wavegrad",
    "Universal Libri-TTS Fullband-MelGAN": "vocoder_models/universal/libri-tts/fullband-melgan",
    "English EK1 WaveGrad": "vocoder_models/en/ek1/wavegrad",
    "English LJSpeech Multiband-MelGAN": "vocoder_models/en/ljspeech/multiband-melgan",
    "English LJSpeech HiFi-GAN v2": "vocoder_models/en/ljspeech/hifigan_v2",
    "English LJSpeech UnivNet": "vocoder_models/en/ljspeech/univnet",
    "English Blizzard2013 HiFi-GAN v2": "vocoder_models/en/blizzard2013/hifigan_v2",
    "English VCTK HiFi-GAN v2": "vocoder_models/en/vctk/hifigan_v2",
    "English SAM HiFi-GAN v2": "vocoder_models/en/sam/hifigan_v2",
    "Dutch MAI Parallel-WaveGAN": "vocoder_models/nl/mai/parallel-wavegan",
    "German Thorsten WaveGrad": "vocoder_models/de/thorsten/wavegrad",
    "German Thorsten Fullband-MelGAN": "vocoder_models/de/thorsten/fullband-melgan",
    "German Thorsten HiFi-GAN v1": "vocoder_models/de/thorsten/hifigan_v1",
    "Japanese Kokoro HiFi-GAN v1": "vocoder_models/ja/kokoro/hifigan_v1",
    "Ukrainian MAI Multiband-MelGAN": "vocoder_models/uk/mai/multiband-melgan",
    "Turkish Common Voice HiFi-GAN": "vocoder_models/tr/common-voice/hifigan",
    "Belarusian Common Voice HiFi-GAN": "vocoder_models/be/common-voice/hifigan",
}

# Helper function to extract text from uploaded files
def extract_text_from_file(file):
    filename = file.filename
    if filename.endswith('.pdf'):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ''
        for page in doc:
            text += page.get_text()
        return text
    elif filename.endswith('.docx'):
        doc = docx.Document(file)
        text = '\n'.join([para.text for para in doc.paragraphs])
        return text
    elif filename.endswith('.txt'):
        return file.read().decode('utf-8')
    else:
        return None

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', tts_models=tts_models, vocoder_models=vocoder_models)

@app.route('/convert', methods=['POST'])
def convert_text_to_speech():
    text = request.form.get('text')
    voice = request.form.get('voice')
    vocoder = request.form.get('vocoder')
    file = request.files.get('file')

    # If a file is uploaded, extract text from it
    if file:
        text = extract_text_from_file(file)
        if not text:
            return jsonify({"error": "Invalid file format"}), 400

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Ensure a valid voice and vocoder is selected
    if voice not in tts_models or vocoder not in vocoder_models:
        return jsonify({"error": "Invalid voice or vocoder selected"}), 400

    # Generate speech using the selected voice and vocoder
    tts = TTS(model_name=tts_models[voice], vocoder_name=vocoder_models[vocoder], progress_bar=False, gpu=False)

    if vocoder:
        tts.load_vocoder(vocoder_name=vocoder_models[vocoder])

    audio_data = BytesIO()
    tts.tts_to_file(text=text, file_path=audio_data)
    audio_data.seek(0)

    # Encode the audio file to base64
    audio_base64 = base64.b64encode(audio_data.read()).decode('utf-8')

    # Return the text and audio as a JSON response
    return jsonify({"text": text, "audio": audio_base64})

if __name__ == '__main__':
    app.run(debug=True)
