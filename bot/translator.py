import os
import re
import json
import requests
import logging
from datetime import datetime
from typing import Optional, Dict, List
from dotenv import load_dotenv
from openai import OpenAI

logger = logging.getLogger(__name__)
load_dotenv()

class AITranslatorChatbot:
    def __init__(self):
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.google_api_key or not self.openai_api_key:
            raise ValueError("GOOGLE_API_KEY or OPENAI_API_KEY not set!")
        
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        self.max_translation_chars = 5000
        self.openai_input_limit = 30000
        self.max_openai_tokens = 2048
        
        # Comprehensive language support
        self.supported_languages = {
            'af': 'Afrikaans', 'ak': 'Twi', 'am': 'Amharic', 'ar': 'Arabic', 'as': 'Assamese', 'ay': 'Aymara',
            'az': 'Azerbaijani', 'bm': 'Bambara', 'be': 'Belarusian', 'bn': 'Bengali', 'bho': 'Bhojpuri',
            'bs': 'Bosnian', 'bg': 'Bulgarian', 'ca': 'Catalan', 'ceb': 'Cebuano', 'ny': 'Chichewa',
            'zh': 'Chinese', 'zh-CN': 'Chinese (Simplified)', 'zh-TW': 'Chinese (Traditional)', 'co': 'Corsican',
            'hr': 'Croatian', 'cs': 'Czech', 'da': 'Danish', 'dv': 'Dhivehi', 'doi': 'Dogri', 'nl': 'Dutch',
            'en': 'English', 'eo': 'Esperanto', 'et': 'Estonian', 'ee': 'Ewe', 'fil': 'Filipino', 'fi': 'Finnish',
            'fr': 'French', 'fy': 'Frisian', 'gl': 'Galician', 'ka': 'Georgian', 'de': 'German', 'el': 'Greek',
            'gn': 'Guarani', 'gu': 'Gujarati', 'ht': 'Haitian Creole', 'ha': 'Hausa', 'haw': 'Hawaiian',
            'he': 'Hebrew', 'hi': 'Hindi', 'hmn': 'Hmong', 'hu': 'Hungarian', 'is': 'Icelandic', 'ig': 'Igbo',
            'ilo': 'Ilocano', 'id': 'Indonesian', 'ga': 'Irish', 'it': 'Italian', 'ja': 'Japanese', 'jw': 'Javanese',
            'kn': 'Kannada', 'kk': 'Kazakh', 'km': 'Khmer', 'rw': 'Kinyarwanda', 'gom': 'Konkani', 'ko': 'Korean',
            'kri': 'Krio', 'ku': 'Kurdish (Kurmanji)', 'ckb': 'Kurdish (Sorani)', 'ky': 'Kyrgyz', 'lo': 'Lao',
            'la': 'Latin', 'lv': 'Latvian', 'ln': 'Lingala', 'lt': 'Lithuanian', 'lg': 'Luganda', 'lb': 'Luxembourgish',
            'mk': 'Macedonian', 'mai': 'Maithili', 'mg': 'Malagasy', 'ms': 'Malay', 'ml': 'Malayalam',
            'mt': 'Maltese', 'mi': 'Maori', 'mr': 'Marathi', 'mni-Mtei': 'Meiteilon (Manipuri)', 'lus': 'Mizo',
            'mn': 'Mongolian', 'my': 'Myanmar (Burmese)', 'ne': 'Nepali', 'no': 'Norwegian', 'or': 'Odia (Oriya)',
            'om': 'Oromo', 'ps': 'Pashto', 'fa': 'Persian', 'pl': 'Polish', 'pt': 'Portuguese', 'pa': 'Punjabi',
            'qu': 'Quechua', 'ro': 'Romanian', 'ru': 'Russian', 'sm': 'Samoan', 'sa': 'Sanskrit',
            'gd': 'Scots Gaelic', 'nso': 'Sepedi', 'sr': 'Serbian', 'st': 'Sesotho', 'sn': 'Shona',
            'sd': 'Sindhi', 'si': 'Sinhala', 'sk': 'Slovak', 'sl': 'Slovenian', 'so': 'Somali', 'es': 'Spanish',
            'su': 'Sundanese', 'sw': 'Swahili', 'sv': 'Swedish', 'tg': 'Tajik', 'ta': 'Tamil', 'tt': 'Tatar',
            'te': 'Telugu', 'th': 'Thai', 'ti': 'Tigrinya', 'ts': 'Tsonga', 'tr': 'Turkish', 'tk': 'Turkmen',
            'uk': 'Ukrainian', 'ur': 'Urdu', 'ug': 'Uyghur', 'uz': 'Uzbek', 'vi': 'Vietnamese', 'cy': 'Welsh',
            'xh': 'Xhosa', 'yi': 'Yiddish', 'yo': 'Yoruba', 'zu': 'Zulu'
        }
        
        self.language_name_to_code = {name.lower(): code for code, name in self.supported_languages.items()}
        self.language_name_to_code.update({
            'español': 'es', 'espagnol': 'es', 'espanhol': 'es', 'français': 'fr', 'deutsch': 'de',
            'italiano': 'it', 'português': 'pt', 'русский': 'ru', '中文': 'zh', '日本語': 'ja',
            '한국어': 'ko', 'العربية': 'ar', 'हिन्दी': 'hi', 'বাংলা': 'bn'
        })
        
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

    def setup_apis(self):
        """Test API connectivity"""
        try:
            test_url = f"https://translation.googleapis.com/language/translate/v2/languages?key={self.google_api_key}"
            response = requests.get(test_url)
            if response.status_code != 200:
                raise Exception(f"Google API test failed: {response.status_code}")
            
            test_response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "Test"}, {"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            if not test_response.choices:
                raise Exception("OpenAI API test failed")
        except Exception as e:
            raise ValueError(f"API setup failed: {str(e)}")

    def detect_language(self, text: str) -> str:
        """Detect language using Google Translate API"""
        try:
            url = f"https://translation.googleapis.com/language/translate/v2/detect?key={self.google_api_key}"
            response = requests.post(url, data={'q': text[:500]})
            if response.status_code == 200:
                result = response.json()
                detected_language = result['data']['detections'][0][0]['language']
                confidence = result['data']['detections'][0][0]['confidence']
                return detected_language if confidence > 0.3 else 'auto'
            logger.error(f"Language detection failed: {response.status_code}")
            return 'auto'
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}")
            return 'auto'

    def smart_text_extraction(self, user_input: str, target_language: str) -> str:
        """Extract translatable text using OpenAI"""
        try:
            prompt = f"""Extract ONLY the content to translate from: "{user_input}"
Target Language: {target_language}
Remove all command words (translate, traduire, অনুবাদ, ترجم), language specs, and instructions.
Examples:
- "translate hello to Spanish" → "hello"
- "good morning in japanese" → "good morning"
- "how do you say thank you in german" → "thank you"
Respond with only the extracted text or "NO_TEXT_FOUND"."""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Extract only translatable content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2048,
                temperature=0.1
            )
            
            extracted_text = response.choices[0].message.content.strip()
            if extracted_text == "NO_TEXT_FOUND" or not extracted_text:
                return self.fallback_text_extraction(user_input)
            
            return extracted_text.strip('"\'')
        except Exception as e:
            logger.error(f"AI text extraction failed: {str(e)}")
            return self.fallback_text_extraction(user_input)

    def fallback_text_extraction(self, user_input: str) -> str:
        """Fallback regex-based text extraction"""
        text = user_input.strip()
        patterns = [
            r'^(?:translate|traduire|অনুবাদ|ترجم|how\s+do\s+you\s+say)\s+(.+?)(?:\s+(?:in|to|into)\s+[a-zA-Z\s]+)?$',
            r'^(.+?)\s+(?:in|to|into)\s+[a-zA-Z\s]+$',
            r'^(.+)$'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return text

    def translate_text(self, text: str, target_language: str, source_language: str = None) -> Dict:
        """Translate text using Google Translate API with chunking"""
        try:
            target_lang_code = self.find_language_code(target_language)
            if not target_lang_code:
                return {
                    'success': False,
                    'error': f"Language '{target_language}' not supported.",
                    'translated_text': None,
                    'source_language': None,
                    'same_language': False,
                    'target_lang_code': None
                }
            
            source_lang_code = self.find_language_code(source_language) if source_language else self.detect_language(text)
            if source_lang_code == target_lang_code:
                return {
                    'success': True,
                    'translated_text': text,
                    'source_language': self.supported_languages.get(source_lang_code, source_lang_code),
                    'same_language': True,
                    'target_lang_code': target_lang_code
                }
            
            if len(text) > self.max_translation_chars:
                chunks = self.split_text_into_chunks(text, self.max_translation_chars)
                translated_chunks = []
                for chunk in chunks:
                    result = self.translate_text(chunk, target_lang_code, source_lang_code)
                    if not result['success']:
                        return result
                    translated_chunks.append(result['translated_text'])
                return {
                    'success': True,
                    'translated_text': ' '.join(translated_chunks),
                    'source_language': self.supported_languages.get(source_lang_code, source_lang_code),
                    'same_language': False,
                    'target_lang_code': target_lang_code
                }
            
            url = f"https://translation.googleapis.com/language/translate/v2?key={self.google_api_key}"
            data = {
                'q': text,
                'target': target_lang_code,
                'source': source_lang_code if source_lang_code != 'auto' else None,
                'format': 'text'
            }
            data = {k: v for k, v in data.items() if v is not None}
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                result = response.json()
                translated_text = result['data']['translations'][0]['translatedText']
                detected_source = result['data']['translations'][0].get('detectedSourceLanguage', source_lang_code)
                return {
                    'success': True,
                    'translated_text': translated_text,
                    'source_language': self.supported_languages.get(detected_source, detected_source),
                    'same_language': False,
                    'target_lang_code': target_lang_code
                }
            return {
                'success': False,
                'error': f"Translation API failed: {response.status_code}",
                'translated_text': None,
                'source_language': None,
                'same_language': False,
                'target_lang_code': None
            }
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            return {
                'success': False,
                'error': f"Translation failed: {str(e)}",
                'translated_text': None,
                'source_language': None,
                'same_language': False,
                'target_lang_code': None
            }

    def split_text_into_chunks(self, text: str, max_chars: int) -> List[str]:
        """Split text into chunks for translation"""
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        current_chunk = ""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        for sentence in sentences:
            if len(sentence) > max_chars:
                words = sentence.split()
                temp_sentence = ""
                for word in words:
                    if len(temp_sentence + word + " ") <= max_chars:
                        temp_sentence += word + " "
                    else:
                        if temp_sentence:
                            chunks.append(temp_sentence.strip())
                        temp_sentence = word + " "
                if temp_sentence:
                    if len(current_chunk + temp_sentence) <= max_chars:
                        current_chunk += temp_sentence
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = temp_sentence
            else:
                if len(current_chunk + sentence) <= max_chars:
                    current_chunk += sentence + " "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + " "
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        return chunks

    def find_language_code(self, language_name: str) -> Optional[str]:
        """Find language code from name"""
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
        return None

    def parse_translation_request(self, user_input: str) -> Dict:
        """Parse translation request using OpenAI"""
        try:
            language_list = ", ".join([f"{name} ({code})" for code, name in sorted(self.supported_languages.items(), key=lambda x: x[1])])
            prompt = f"""Parse the translation request: "{user_input[:self.openai_input_limit]}"
Available Languages: {language_list[:2000]}...
1. Identify if it's a translation request (explicit or implicit).
2. Extract the text to translate and target language.
3. Handle typos in language names.
Respond in JSON:
{{
    "is_translation_request": true/false,
    "text": "text to translate or null",
    "target_language": "language name or null",
    "confidence": 0.0-1.0
}}"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Parse translation requests and return JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_openai_tokens,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            if result.get('is_translation_request', False) and result.get('text') and result.get('target_language'):
                text = self.smart_text_extraction(user_input, result['target_language'])
                if not text or text.strip() == "":
                    text = self.fallback_text_extraction(user_input)
                return {
                    'is_translation_request': True,
                    'text': text,
                    'target_language': result['target_language'],
                    'conversational_response': f"I'll translate '{text}' to {result['target_language'].title()} for you!"
                }
            
            return {
                'is_translation_request': False,
                'text': None,
                'target_language': None,
                'conversational_response': "Please provide a valid translation request, e.g., 'Text in Spanish' or 'Translate hello to French'."
            }
        except Exception as e:
            logger.error(f"AI parsing failed: {str(e)}")
            return self.fallback_parse(user_input)

    def fallback_parse(self, user_input: str) -> Dict:
        """Fallback regex-based parsing"""
        user_input = user_input.strip()
        if user_input.lower().endswith('to all languages') or user_input.lower().endswith('in all languages'):
            text_to_translate = user_input[:user_input.lower().rindex('to all languages')].strip() or \
                              user_input[:user_input.lower().rindex('in all languages')].strip()
            if text_to_translate:
                return {
                    'is_translation_request': True,
                    'text': text_to_translate,
                    'target_language': 'all',
                    'conversational_response': f"I'll translate '{text_to_translate}' to all supported languages."
                }
        
        all_prepositions = '|'.join([prep for lang_preps in self.prepositions.values() for prep in lang_preps])
        language_names = list(self.supported_languages.values()) + list(self.language_name_to_code.keys())
        language_names = [re.escape(name) for name in language_names]
        language_pattern = '|'.join(language_names)
        
        patterns = [
            rf'(.+?)\s+(?:{all_prepositions})\s+({language_pattern})\b(?:\.|!|\?|$)',
            rf'translate\s+(.+?)\s+(?:{all_prepositions})\s+({language_pattern})\b(?:\.|!|\?|$)',
            rf'(.+?)\s+({language_pattern})\b(?:\.|!|\?|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                text_to_translate = match.group(1).strip()
                target_language = match.group(2).strip().rstrip('.!?')
                if text_to_translate:
                    return {
                        'is_translation_request': True,
                        'text': text_to_translate,
                        'target_language': target_language,
                        'conversational_response': f"I'll translate '{text_to_translate}' to {target_language.title()} for you!"
                    }
        
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
        """Handle translation request, matching original response format"""
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
        
        translation_result = self.translate_text(text_to_translate, target_language)
        
        if not translation_result['success']:
            return {
                'success': False,
                'translated_text': None,
                'conversational_response': translation_result['error'],
                'target_language': target_language
            }
        
        return {
            'success': True,
            'translated_text': translation_result['translated_text'],
            'conversational_response': translation_result['translated_text'],
            'target_language': target_language,
            'translation_result': {
                'success': translation_result['success'],
                'translated_text': translation_result['translated_text'],
                'source_language': translation_result['source_language'],
                'same_language': translation_result.get('same_language', False),
                'error': translation_result.get('error'),
                'target_lang_code': translation_result['target_lang_code']
            }
        }