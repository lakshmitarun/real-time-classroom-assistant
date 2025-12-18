import json
import os
import csv

class TranslationService:
    def __init__(self):
        self.translation_db = self._load_translation_database()
    
    def _load_translation_database(self):
        """Load translation database from CSV file"""
        db = {'english': {}, 'bodo': {}, 'mizo': {}}
        
        # Try to load from the comprehensive dataset
        csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'classroom_dataset_complete.csv')
        
        if os.path.exists(csv_path):
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        english = row['English'].lower().strip()
                        bodo = row['Bodo'].strip()
                        mizo = row['Mizo'].strip()
                        
                        # Add to English index
                        db['english'][english] = {'bodo': bodo, 'mizo': mizo}
                        
                        # Debug: print if we find tarun
                        if english == 'tarun':
                            print(f"DEBUG: Found tarun -> {bodo}")
                        
                        # Add to Bodo index
                        db['bodo'][bodo.lower()] = {'english': english.capitalize(), 'mizo': mizo}
                        
                        # Add to Mizo index
                        db['mizo'][mizo.lower()] = {'english': english.capitalize(), 'bodo': bodo}
                
                print(f"[SUCCESS] Loaded {len(db['english'])} translations from CSV")
                return db
            except Exception as e:
                print(f"[WARNING] Error loading CSV: {e}")
        
        # Fallback to hardcoded translations
        print("[WARNING] Using fallback translation database")
        return {
            'english': {
                'good morning class': {'bodo': 'सुबुं बिहान', 'mizo': 'Zing tlâm ṭha class'},
                'please open your books': {'bodo': 'अननानै नायनि किताबखौ खेव', 'mizo': 'I lehkhabu hung hawng rawh'},
                'do you understand?': {'bodo': 'नों गोजौ खायला?', 'mizo': 'I hrethiam em?'},
                'today we will learn mathematics': {'bodo': 'दिनै बे सान्न्रि होननाय गोनां', 'mizo': 'Tunah Mathematics kan zir dawn'},
                'very good, well done': {'bodo': 'बेयै गोजौ', 'mizo': 'A tha hle'},
                'please be quiet': {'bodo': 'अननानै थिरगोन दङ', 'mizo': 'Dâwiin dâi la'},
                'raise your hand': {'bodo': 'नायनि खुन्थाखौ थोन', 'mizo': 'I kut kalh rawh'},
                'listen carefully': {'bodo': 'मोनो खालाम', 'mizo': 'Ngaithla ṭha rawh'},
                'write this down': {'bodo': 'बेखौ लिरगोन', 'mizo': 'Hei hi ziak rawh'},
                'homework for tomorrow': {'bodo': 'गाबै नुजाथाव जागायनाय गिबि', 'mizo': 'Tukleha tan homework'},
                'excellent work': {'bodo': 'गोजौ लाफा', 'mizo': 'Ṭha tak tak'},
                'sit down please': {'bodo': 'अननानै फुं', 'mizo': 'Thu rawh le'},
                'pay attention': {'bodo': 'मोनो खालाम', 'mizo': 'Ngaithla ṭha rawh'},
                'turn to page': {'bodo': 'फेजखौ हुं', 'mizo': 'Phek kaltlang rawh'},
                'let us begin': {'bodo': 'जिउनां जागाय', 'mizo': 'Kan tan dawn e'},
                'mathematics': {'bodo': 'सान्न्रि', 'mizo': 'Mathematics'},
                'science': {'bodo': 'बिजान', 'mizo': 'Science'},
                'history': {'bodo': 'बुरुं', 'mizo': 'History'},
                'geography': {'bodo': 'फिथा बिजान', 'mizo': 'Geography'},
                'english': {'bodo': 'आंग्रेजी', 'mizo': 'English'},
                'hello': {'bodo': 'सुबुं', 'mizo': 'Chibai'},
                'thank you': {'bodo': 'मोजां', 'mizo': 'Ka lawm e'},
                'yes': {'bodo': 'अं', 'mizo': 'Awle'},
                'no': {'bodo': 'नङा', 'mizo': 'Aih'},
                'please help me': {'bodo': 'अननानै आङा मद्द खालाम', 'mizo': 'Min pui ve rawh'},
                'i dont understand': {'bodo': 'आं गोजाखै', 'mizo': 'Ka hrethiam lo'},
                'repeat please': {'bodo': 'अननानै बार हुनाय', 'mizo': 'Nawn lehah sawi leh rawh'},
                'speak slowly': {'bodo': 'थायनै राव', 'mizo': 'Zawi deuh in sawi rawh'},
                'test tomorrow': {'bodo': 'गाबै परिखा', 'mizo': 'Tukleha test'},
                'study hard': {'bodo': 'गोजौनै होनना', 'mizo': 'Chak takin zir rawh'}
            },
            'bodo': {
                'सुबुं बिहान': {'english': 'Good morning', 'mizo': 'Zing tlâm ṭha'},
                'अननानै नायनि किताबखौ खेव': {'english': 'Please open your books', 'mizo': 'I lehkhabu hung hawng rawh'},
                'नों गोजौ खायला?': {'english': 'Do you understand?', 'mizo': 'I hrethiam em?'},
                'बेयै गोजौ': {'english': 'Very good', 'mizo': 'A tha hle'},
                'सुबुं': {'english': 'Hello', 'mizo': 'Chibai'},
                'मोजां': {'english': 'Thank you', 'mizo': 'Ka lawm e'},
                'अं': {'english': 'Yes', 'mizo': 'Awle'},
                'नङा': {'english': 'No', 'mizo': 'Aih'},
                'सान्न्रि': {'english': 'Mathematics', 'mizo': 'Mathematics'},
                'बिजान': {'english': 'Science', 'mizo': 'Science'}
            },
            'mizo': {
                'zing tlâm ṭha': {'english': 'Good morning', 'bodo': 'सुबुं बिहान'},
                'i lehkhabu hung hawng rawh': {'english': 'Please open your books', 'bodo': 'अननानै नायनि किताबखौ खेव'},
                'i hrethiam em?': {'english': 'Do you understand?', 'bodo': 'नों गोजौ खायला?'},
                'a tha hle': {'english': 'Very good', 'bodo': 'बेयै गोजौ'},
                'chibai': {'english': 'Hello', 'bodo': 'सुबुं'},
                'ka lawm e': {'english': 'Thank you', 'bodo': 'मोजां'},
                'awle': {'english': 'Yes', 'bodo': 'अं'},
                'aih': {'english': 'No', 'bodo': 'नङा'},
                'mathematics': {'english': 'Mathematics', 'bodo': 'सान्न्रि'},
                'science': {'english': 'Science', 'bodo': 'बिजान'}
            }
        }
    
    def translate(self, text, source_lang, target_lang):
        """Translate text from source language to target language"""
        if not text:
            return ''
        
        # Normalize input
        text_lower = text.lower().strip()
        source_lang = source_lang.lower()
        target_lang = target_lang.lower()
        
        # If source and target are the same, return original text
        if source_lang == target_lang:
            return text
        
        # Try exact match first
        if source_lang in self.translation_db:
            if text_lower in self.translation_db[source_lang]:
                translation_entry = self.translation_db[source_lang][text_lower]
                if target_lang in translation_entry:
                    return translation_entry[target_lang]
        
        # Fallback: Try word-by-word translation
        words = text_lower.split()
        translated_words = []
        
        for word in words:
            # Remove punctuation for lookup
            clean_word = word.strip('.,!?;:')
            
            if source_lang in self.translation_db and clean_word in self.translation_db[source_lang]:
                translation_entry = self.translation_db[source_lang][clean_word]
                if target_lang in translation_entry:
                    translated_words.append(translation_entry[target_lang])
                else:
                    translated_words.append(word)
            else:
                translated_words.append(word)
        
        # If at least one word was translated, return the result
        translated_text = ' '.join(translated_words)
        if translated_text.lower() != text_lower:
            return translated_text
        
        # Final fallback: return empty string (not found in dataset)
        return ''
    
    def get_supported_languages(self):
        """Get list of supported languages"""
        return ['english', 'bodo', 'mizo']
    
    def add_translation(self, text, source_lang, target_lang, translation):
        """Add new translation to database"""
        text_lower = text.lower().strip()
        source_lang = source_lang.lower()
        target_lang = target_lang.lower()
        
        if source_lang not in self.translation_db:
            self.translation_db[source_lang] = {}
        
        if text_lower not in self.translation_db[source_lang]:
            self.translation_db[source_lang][text_lower] = {}
        
        self.translation_db[source_lang][text_lower][target_lang] = translation
        return True
