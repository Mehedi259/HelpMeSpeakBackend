import os
import re
import requests
import logging
from dotenv import load_dotenv
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)
load_dotenv()

class AITranslatorChatbot:
    def __init__(self):
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set!")
        self.supported_languages = {}
        self.prepositions = {
            'en': ['in', 'to', 'into'],
            'es': ['en', 'a', 'hacia'],
            'fr': ['en', 'à', 'vers'],
            'de': ['in', 'zu', 'nach'],
            'it': ['in', 'a', 'verso'],
            'pt': ['em', 'para', 'a'],
            'ru': ['в', 'на', 'к'],
            'zh': ['在', '到'],
            'ja': ['に', 'へ'],
            'ko': ['에', '으로'],
            'ar': ['في', 'إلى'],
            'hi': ['में', 'को'],
            'bn': ['এ', 'থেকে']
        }
        self.language_name_to_code = {
            'english': 'en', 'spanish': 'es', 'french': 'fr', 'german': 'de',
            'italian': 'it', 'portuguese': 'pt', 'russian': 'ru', 'chinese': 'zh',
            'japanese': 'ja', 'korean': 'ko', 'arabic': 'ar', 'hindi': 'hi',
            'bengali': 'bn', 'español': 'es', 'espagnol': 'es', 'espanhol': 'es',
            'français': 'fr', 'deutsch': 'de', 'italiano': 'it', 'português': 'pt',
            'русский': 'ru', '中文': 'zh', '日本語': 'ja', '한국어': 'ko',
            'العربية': 'ar', 'हिन्दी': 'hi', 'বাংলা': 'bn',
            'dutch': 'nl', 'swedish': 'sv', 'norwegian': 'no', 'danish': 'da',
            'finnish': 'fi', 'polish': 'pl', 'turkish': 'tr', 'greek': 'el',
            'hebrew': 'iw', 'thai': 'th', 'vietnamese': 'vi', 'indonesian': 'id',
            'malay': 'ms', 'urdu': 'ur', 'tamil': 'ta', 'telugu': 'te',
            'gujarati': 'gu', 'kannada': 'kn', 'malayalam': 'ml', 'marathi': 'mr',
            'punjabi': 'pa'
        }
        self.load_supported_languages()

    def setup_apis(self):
        """Setup API clients"""
        try:
            test_url = f"https://translation.googleapis.com/language/translate/v2/languages?key={self.google_api_key}"
            response = requests.get(test_url)
            if response.status_code != 200:
                raise Exception(f"Google API key test failed: {response.status_code}")
        except Exception as e:
            raise ValueError(f"Error testing Google API: {str(e)}")

    def load_supported_languages(self):
        """Load supported languages from Google Translate API"""
        try:
            url = f"https://translation.googleapis.com/language/translate/v2/languages?key={self.google_api_key}&target=en"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                languages = data['data']['languages']
                self.supported_languages = {lang['language']: lang.get('name', lang['language']) for lang in languages}
                logger.info(f"Loaded {len(self.supported_languages)} supported languages")
            else:
                raise Exception(f"API request failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Error loading supported languages: {str(e)}")
            self.supported_languages = {
                'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
                'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'zh': 'Chinese',
                'ja': 'Japanese', 'ko': 'Korean', 'ar': 'Arabic', 'hi': 'Hindi',
                'bn': 'Bengali', 'nl': 'Dutch', 'sv': 'Swedish', 'no': 'Norwegian',
                'da': 'Danish', 'fi': 'Finnish', 'pl': 'Polish', 'tr': 'Turkish',
                'el': 'Greek', 'iw': 'Hebrew', 'th': 'Thai', 'vi': 'Vietnamese',
                'id': 'Indonesian', 'ms': 'Malay', 'ur': 'Urdu', 'ta': 'Tamil',
                'te': 'Telugu', 'gu': 'Gujarati', 'kn': 'Kannada', 'ml': 'Malayalam',
                'mr': 'Marathi', 'pa': 'Punjabi'
            }

    def find_language_code(self, language_name: str) -> Optional[str]:
        """Find language code from language name"""
        if not language_name:
            return None
        language_name = language_name.lower().strip().rstrip('.!?')
        if language_name in self.supported_languages:
            return language_name
        if language_name in self.language_name_to_code:
            return self.language_name_to_code[language_name]
        for code, name in self.supported_languages.items():
            if language_name == name.lower() or language_name in name.lower():
                return code
        logger.debug(f"No language code found for: {language_name}")
        return None

    def detect_language(self, text: str) -> str:
        """Detect the language of given text"""
        try:
            url = f"https://translation.googleapis.com/language/translate/v2/detect?key={self.google_api_key}"
            response = requests.post(url, data={'q': text})
            if response.status_code == 200:
                result = response.json()
                detected_language = result['data']['detections'][0][0]['language']
                confidence = result['data']['detections'][0][0]['confidence']
                logger.debug(f"Detected language: {detected_language}, confidence: {confidence}")
                return detected_language if confidence > 0.5 else 'en'
            return 'en'
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}")
            return 'en'

    def translate_text(self, text: str, target_language: str, source_language: str = None) -> Dict:
        """Translate text using Google Translate API"""
        max_chunk_size = 5000
        if len(text) > max_chunk_size:
            chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
            translated_chunks = []
            for chunk in chunks:
                result = self.translate_text(chunk, target_language, source_language)
                if not result['success']:
                    return result
                translated_chunks.append(result['translated_text'])
            return {
                'success': True,
                'translated_text': ''.join(translated_chunks),
                'source_language': result['source_language'],
                'target_language': result['target_language'],
                'same_language': result['same_language'],
                'target_lang_code': result['target_lang_code'],
                'error': None
            }
        try:
            target_lang_code = self.find_language_code(target_language)
            if not target_lang_code:
                logger.error(f"Unsupported language: {target_language}")
                return {
                    'success': False,
                    'error': f"Language '{target_language}' not supported.",
                    'translated_text': None,
                    'source_language': None,
                    'target_language': target_language,
                    'target_lang_code': None
                }
            source_lang_code = self.find_language_code(source_language) if source_language else self.detect_language(text)
            if source_lang_code == target_lang_code:
                return {
                    'success': True,
                    'translated_text': text,
                    'source_language': self.supported_languages.get(source_lang_code, source_lang_code),
                    'target_language': self.supported_languages.get(target_lang_code, target_language),
                    'same_language': True,
                    'target_lang_code': target_lang_code
                }
            url = f"https://translation.googleapis.com/language/translate/v2?key={self.google_api_key}"
            data = {
                'q': text,
                'target': target_lang_code,
                'source': source_lang_code,
                'format': 'text'
            }
            response = requests.post(url, data=data)
            if response.status_code == 200:
                result = response.json()
                translated_text = result['data']['translations'][0]['translatedText']
                return {
                    'success': True,
                    'translated_text': translated_text,
                    'source_language': self.supported_languages.get(source_lang_code, source_lang_code),
                    'target_language': self.supported_languages.get(target_lang_code, target_language),
                    'same_language': False,
                    'target_lang_code': target_lang_code
                }
            logger.error(f"Translation API failed: {response.status_code}")
            return {
                'success': False,
                'error': f"Translation API failed: {response.status_code}",
                'translated_text': None,
                'source_language': None,
                'target_language': target_language,
                'target_lang_code': None
            }
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            return {
                'success': False,
                'error': f"Translation failed: {str(e)}",
                'translated_text': None,
                'source_language': None,
                'target_language': target_language,
                'target_lang_code': None
            }

    def parse_translation_request(self, user_input: str) -> Dict:
        """Parse translation requests with language at the end in any supported language"""
        logger.debug(f"Parsing input: '{user_input}'")
        user_input = user_input.strip()

        # Handle "translate to all languages" request
        if user_input.lower().endswith('to all languages') or user_input.lower().endswith('in all languages'):
            text_to_translate = user_input[:user_input.lower().rindex('to all languages')].strip() or \
                              user_input[:user_input.lower().rindex('in all languages')].strip()
            if text_to_translate:
                logger.debug(f"All languages request: '{text_to_translate}'")
                return {
                    'is_translation_request': True,
                    'text': text_to_translate,
                    'target_language': 'all',
                    'conversational_response': f"I'll translate '{text_to_translate}' to all supported languages."
                }

        # Combine all prepositions into a single regex group
        all_prepositions = '|'.join([prep for lang_preps in self.prepositions.values() for prep in lang_preps])

        # Create a regex pattern for language names from supported_languages and language_name_to_code
        language_names = list(self.supported_languages.values()) + list(self.language_name_to_code.keys())
        language_names = [re.escape(name) for name in language_names]
        language_pattern = '|'.join(language_names)

        # Patterns to match
        patterns = [
            rf'(.+?)\s+(?:{all_prepositions})\s+({language_pattern})\b(?:\.|!|\?|$)',
            rf'translate\s+(.+?)\s+(?:{all_prepositions})\s+({language_pattern})\b(?:\.|!|\?|$)',
            rf'say\s+(.+?)\s+(?:{all_prepositions})\s+({language_pattern})\b(?:\.|!|\?|$)',
            rf'convert\s+(.+?)\s+(?:{all_prepositions})\s+({language_pattern})\b(?:\.|!|\?|$)',
            rf'how\s+do\s+you\s+say\s+(.+?)\s+(?:{all_prepositions})\s+({language_pattern})\b(?:\.|!|\?|$)',
            rf'what\s+is\s+(.+?)\s+(?:{all_prepositions})\s+({language_pattern})\b(?:\.|!|\?|$)',
            rf'(.+?)\s+({language_pattern})\b(?:\.|!|\?|$)'  # No preposition
        ]

        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                text_to_translate = match.group(1).strip()
                target_language = match.group(2).strip().rstrip('.!?')
                language_code = self.find_language_code(target_language)
                if text_to_translate and language_code:
                    logger.debug(f"Matched pattern: {pattern}, text: '{text_to_translate}', target: '{target_language}', code: '{language_code}'")
                    return {
                        'is_translation_request': True,
                        'text': text_to_translate,
                        'target_language': target_language,
                        'conversational_response': f"I'll translate '{text_to_translate}' to {target_language.title()} for you!"
                    }
                logger.debug(f"Language code not found for: {target_language}")

        logger.debug("No match found for input")
        return {
            'is_translation_request': False,
            'text': None,
            'target_language': None,
            'conversational_response': "Please provide a valid translation request, e.g., 'Text in Spanish' or 'Translate hello to French'."
        }

    def translate_to_all_languages(self, text: str, source_language: str = None) -> Dict:
        """Translate text to all supported languages"""
        translations = {}
        for lang_code in self.supported_languages.keys():
            result = self.translate_text(text, lang_code, source_language)
            translations[lang_code] = result
        return translations

    def handle_translation_request(self, user_input: str) -> Dict:
        """Handle translation request, ensuring target language name is not translated and is hidden in output"""
        parse_result = self.parse_translation_request(user_input)
        
        if not parse_result['is_translation_request']:
            return {
                'success': False,
                'translated_text': None,
                'conversational_response': parse_result['conversational_response'],
                'target_language': None
            }
        
        text_to_translate = parse_result['text']
        target_language = parse_result['target_language']
        
        # Handle translation to all languages
        if target_language == 'all':
            translations = self.translate_to_all_languages(text_to_translate)
            result = {
                'success': True,
                'translated_text': {
                    self.supported_languages.get(lang_code, lang_code): data['translated_text'] 
                    for lang_code, data in translations.items() if data['success']
                },
                'conversational_response': f"Translated '{text_to_translate}' to all supported languages.",
                'target_language': 'all'
            }
            return result
        
        # Handle translation to a single language
        translation_result = self.translate_text(text_to_translate, target_language)
        
        if not translation_result['success']:
            return {
                'success': False,
                'translated_text': None,
                'conversational_response': translation_result['error'],
                'target_language': target_language
            }
        
        # Return only the translated text, hiding the target language
        return {
            'success': True,
            'translated_text': translation_result['translated_text'],
            'conversational_response': translation_result['translated_text'],  # Only the translated text is shown
            'target_language': target_language  # Kept for internal use but not shown in conversational_response
        }