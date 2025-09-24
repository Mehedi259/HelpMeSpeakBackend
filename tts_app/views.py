import os
import uuid
import base64
import requests
import re
import logging
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.http import HttpResponse

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class TranslateAndTTSAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def clean_text_for_tts(self, text: str) -> str:
        """Clean text for TTS by removing problematic characters and limiting length."""
        # Remove underscores and excessive punctuation, preserve Bengali script
        cleaned_text = re.sub(r'[_;]', ' ', text)  # Replace underscores and semicolons with spaces
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()  # Normalize spaces
        # Limit to 5000 characters (Google TTS limit)
        max_chars = 5000
        if len(cleaned_text) > max_chars:
            logger.warning(f"Text truncated from {len(cleaned_text)} to {max_chars} characters")
            cleaned_text = cleaned_text[:max_chars]
        return cleaned_text

    def get_best_voice_for_language(self, language_code: str) -> dict | None:
        """Get the best available voice for a language, preferring Chirp3-HD female voices."""
        try:
            url = f"https://texttospeech.googleapis.com/v1/voices?key={settings.GOOGLE_API_KEY}"
            logger.debug(f"Fetching voices for language: {language_code}")
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            voices = data.get('voices', [])

            # Filter voices for the target language
            matching_voices = [
                voice for voice in voices
                if any(lang_code.startswith(language_code) for lang_code in voice['languageCodes'])
            ]

            logger.debug(f"Matching voices for {language_code}: {len(matching_voices)} found")

            if not matching_voices:
                logger.warning(f"No voices found for language: {language_code}")
                return None

            # Priority order: Chirp3-HD Female > Chirp3-HD Male > Neural2 Female > Neural2 Male > Standard Female > Standard Male
            priorities = [
                ('Chirp3-HD', 'FEMALE'),
                ('Chirp3-HD', 'MALE'),
                ('Neural2', 'FEMALE'),
                ('Neural2', 'MALE'),
                ('Standard', 'FEMALE'),
                ('Standard', 'MALE')
            ]

            for voice_type, gender in priorities:
                for voice in matching_voices:
                    if voice_type in voice.get('name', '') and voice.get('ssmlGender') == gender:
                        logger.info(f"Selected voice: {voice['name']}, Type: {voice_type}, Gender: {gender}")
                        return {
                            'name': voice['name'],
                            'language_code': voice['languageCodes'][0],
                            'gender': voice['ssmlGender'],
                            'type': voice_type
                        }

            # Fallback to first available voice
            voice = matching_voices[0]
            logger.info(f"Fallback voice selected: {voice['name']}, Type: {'Chirp3-HD' if 'Chirp3-HD' in voice['name'] else 'Neural2' if 'Neural2' in voice['name'] else 'Standard'}, Gender: {voice.get('ssmlGender', 'NEUTRAL')}")
            return {
                'name': voice['name'],
                'language_code': voice['languageCodes'][0],
                'gender': voice.get('ssmlGender', 'NEUTRAL'),
                'type': 'Chirp3-HD' if 'Chirp3-HD' in voice['name'] else (
                    'Neural2' if 'Neural2' in voice['name'] else 'Standard'
                )
            }

        except Exception as e:
            logger.error(f"Error getting voice for {language_code}: {str(e)}")
            return None

    def text_to_speech(self, text: str, language_code: str) -> str | None:
        """Convert text to speech using Google TTS API with Chirp3-HD female voice preference."""
        try:
            # Clean text for TTS
            cleaned_text = self.clean_text_for_tts(text)
            logger.debug(f"Cleaned text for TTS: {cleaned_text[:100]}...")

            # Get the best voice for this language
            voice_config = self.get_best_voice_for_language(language_code)
            if not voice_config:
                logger.warning(f"No voice available for {language_code}")
                return f"not found audio (No voice available for {language_code})"

            # Create media directory if it doesn't exist
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            file_name = f"{uuid.uuid4()}_{language_code}.mp3"
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)

            # Prepare TTS request
            url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={settings.GOOGLE_API_KEY}"
            payload = {
                "input": {"text": cleaned_text},
                "voice": {
                    "languageCode": voice_config['language_code'],
                    "name": voice_config['name']
                },
                "audioConfig": {
                    "audioEncoding": "MP3",
                    "pitch": 0.0,
                    "speakingRate": .9
                }
            }
            headers = {"Content-Type": "application/json"}
            logger.debug(f"TTS request payload: {payload}")
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            audio_content = result.get('audioContent')
            if not audio_content:
                logger.error("No audio content received from TTS API")
                return "not found audio (No audio content received)"

            # Save audio file
            audio_data = base64.b64decode(audio_content)
            with open(file_path, 'wb') as audio_file:
                audio_file.write(audio_data)
            logger.info(f"Audio file saved: {file_path}")

            # Return the audio URL
            audio_url = self.request.build_absolute_uri(settings.MEDIA_URL + file_name)
            logger.info(f"Audio URL: {audio_url}")
            return audio_url

        except requests.exceptions.HTTPError as e:
            error_message = f"TTS error for {language_code}: {str(e)}"
            if response.status_code == 400:
                error_message += " (Possibly due to unsupported characters or invalid voice)"
                try:
                    error_details = response.json()
                    logger.error(f"TTS error details: {error_details}")
                except ValueError:
                    pass
            logger.error(error_message)
            return f"not found audio ({error_message})"
        except Exception as e:
            logger.error(f"TTS error for {language_code}: {str(e)}")
            return f"not found audio (TTS error: {str(e)})"

    def post(self, request):
        text = request.data.get("text")
        lang_code = request.data.get("lang") or request.data.get("target_lang")

        if not text:
            return Response({"error": "No text provided."}, status=400)
        if not lang_code:
            return Response({"error": "No language selected."}, status=400)

        # Google Translate API
        API_URL = "https://translation.googleapis.com/language/translate/v2"
        try:
            API_KEY = settings.GOOGLE_API_KEY
            logger.debug(f"Using GOOGLE_API_KEY: {API_KEY[:4]}...{API_KEY[-4:]}")
        except AttributeError:
            logger.error("GOOGLE_API_KEY not configured in settings.")
            return Response({"error": "GOOGLE_API_KEY not configured in settings."}, status=500)

        try:
            payload = {"q": text, "target": lang_code}
            headers = {"Content-Type": "application/json"}
            logger.debug(f"Translation request payload: {payload}")
            response = requests.post(f"{API_URL}?key={API_KEY}", json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            translated_text = result["data"]["translations"][0]["translatedText"]
            logger.info(f"Translated text: {translated_text}")
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            return Response({"error": f"Translation failed: {str(e)}"}, status=500)

        # Generate audio using Google TTS with Chirp3-HD female voice preference
        audio_url = self.text_to_speech(translated_text, lang_code)

        return Response({
            "original_text": text,
            "translated_text": translated_text,
            "audio_url": audio_url
        })

def home(request):
    return HttpResponse("Welcome to Help Me Speak")