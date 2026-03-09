import json
import os
import csv
import re

class TranslationService:
    def __init__(self):
        self.translation_db = self._load_translation_database()
    
    def _normalize_text(self, text, lang='english'):
        """Normalize text for searching"""
        if not text:
            return ''
        text = text.strip()
        # For English and Mizo, use lowercase. For Bodo, preserve case (Devanagari script)
        if lang in ['english', 'mizo']:
            text = text.lower()
        return text
    
    def _load_translation_database(self):
        """Load translation database from CSV file with improved error handling"""
        db = {'english': {}, 'bodo': {}, 'mizo': {}}
        
        # Try to load from the comprehensive dataset
        csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'classroom_dataset_complete.csv')
        
        if os.path.exists(csv_path):
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    count = 0
                    skipped = 0
                    
                    for row in reader:
                        try:
                            # Handle both column names (ID,English,Bodo,Mizo,Category format)
                            english = row.get('English', '').strip()
                            bodo = row.get('Bodo', '').strip()
                            mizo = row.get('Mizo', '').strip()
                            
                            # Skip empty entries
                            if not english and not bodo and not mizo:
                                skipped += 1
                                continue
                            
                            # Add to English index (lowercase for case-insensitive search)
                            if english:
                                english_lower = self._normalize_text(english, 'english')
                                if english_lower not in db['english']:
                                    db['english'][english_lower] = {'bodo': bodo, 'mizo': mizo}
                            
                            # Add to Bodo index (exact case preservation for Devanagari)
                            if bodo and bodo != '?':  # Skip placeholder values
                                if bodo not in db['bodo']:
                                    db['bodo'][bodo] = {'english': english.capitalize() if english else '', 'mizo': mizo}
                            
                            # Add to Mizo index (lowercase for case-insensitive search)
                            if mizo and mizo != '?':  # Skip placeholder values
                                mizo_lower = self._normalize_text(mizo, 'mizo')
                                if mizo_lower not in db['mizo']:
                                    db['mizo'][mizo_lower] = {'english': english.capitalize() if english else '', 'bodo': bodo}
                            
                            count += 1
                        except Exception as row_error:
                            skipped += 1
                            continue
                
                print(f"[SUCCESS] Loaded {count} translations from CSV")
                print(f"  - English entries: {len(db['english'])}")
                print(f"  - Bodo entries: {len(db['bodo'])}")
                print(f"  - Mizo entries: {len(db['mizo'])}")
                print(f"  - Skipped: {skipped}")
                
                # Show sample entries (safe for console output)
                if db['bodo']:
                    try:
                        print(f"  - Sample Bodo entry loaded successfully")
                    except:
                        pass  # Ignore encoding errors in console output
                
                return db
            except Exception as e:
                print(f"[WARNING] Error loading CSV: {e}")
                import traceback
                traceback.print_exc()
        
        # Fallback to hardcoded translations
        print("[WARNING] Using fallback translation database")
        return {
            'english': {
                # Phrases
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
                'what are you doing': {'bodo': 'नों तुइ तिङ गोबा', 'mizo': 'I ti tawng law em'},
                'hi hello what are you doing': {'bodo': 'सुबुं, नों तुइ तिङ गोबा', 'mizo': 'Chibai, i ti tawng law em'},
                # Single words
                'mathematics': {'bodo': 'सान्न्रि', 'mizo': 'Mathematics'},
                'science': {'bodo': 'बिजान', 'mizo': 'Science'},
                'history': {'bodo': 'बुरुं', 'mizo': 'History'},
                'geography': {'bodo': 'फिथा बिजान', 'mizo': 'Geography'},
                'english': {'bodo': 'आंग्रेजी', 'mizo': 'English'},
                'hello': {'bodo': 'सुबुं', 'mizo': 'Chibai'},
                'hi': {'bodo': 'सुबुं', 'mizo': 'Chibai'},
                'thank you': {'bodo': 'मोजां', 'mizo': 'Ka lawm e'},
                'thanks': {'bodo': 'मोजां', 'mizo': 'Ka lawm e'},
                'yes': {'bodo': 'अं', 'mizo': 'Awle'},
                'no': {'bodo': 'नङा', 'mizo': 'Aih'},
                'you': {'bodo': 'नों', 'mizo': 'I'},
                'are': {'bodo': 'खायला', 'mizo': 'law'},
                'doing': {'bodo': 'गोबा', 'mizo': 'tawng'},
                'what': {'bodo': 'कोन', 'mizo': 'ti'},
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
                'बिजान': {'english': 'Science', 'mizo': 'Science'},
                'नायनि फोरमाखौ खेव': {'english': 'Open your notebooks', 'mizo': 'I lehkhabu hawng rawh'},
                'नायनि किताबखौ बन्द थ': {'english': 'Close your books', 'mizo': 'I lehkhabu khar rawh'},
                'अननानै फुं': {'english': 'Sit down please', 'mizo': 'Thu rawh le'},
                'गासै दिंना': {'english': 'Stand up everyone', 'mizo': 'Mi zawng ding rawh'},
                'नों': {'english': 'You', 'mizo': 'I'},
                'तुइ': {'english': 'Are', 'mizo': 'law'},
                'गोबा': {'english': 'Doing', 'mizo': 'tawng'},
                'सुबुं मा नं थां दङ': {'english': 'Good morning, how are you?', 'mizo': 'Zing tlâm ṭha, i ni ṭha em?'}
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
                'science': {'english': 'Science', 'bodo': 'बिजान'},
                'i lehkhabu hawng rawh': {'english': 'Open your notebooks', 'bodo': 'नायनि फोरमाखौ खेव'},
                'i lehkhabu khar rawh': {'english': 'Close your books', 'bodo': 'नायनि किताबखौ बन्द थ'},
                'thu rawh le': {'english': 'Sit down please', 'bodo': 'अननानै फुं'},
                'mi zawng ding rawh': {'english': 'Stand up everyone', 'bodo': 'गासै दिंना'}
            }
        }
    
    def _partial_match_search(self, text_normalized, db_dict, lang='english'):
        """Search for partial/fuzzy matches if exact match fails"""
        best_match = None
        best_score = 0
        
        # For English/Mizo, use lowercase comparison
        if lang in ['english', 'mizo']:
            text_search = text_normalized.lower()
            for key in db_dict:
                if key.lower() in text_search or text_search in key.lower():
                    # Calculate match score (prioritize exact substring over partial)
                    if key.lower() == text_search:
                        return key, db_dict[key], 1.0
                    elif key.lower() in text_search:
                        score = len(key) / len(text_search)
                        if score > best_score:
                            best_match = key
                            best_score = score
        else:
            # For Bodo (Devanagari), use exact matching only
            for key in db_dict:
                if key in text_normalized:
                    return key, db_dict[key], 1.0
                elif text_normalized in key:
                    # Partial match
                    score = len(text_normalized) / len(key)
                    if score > best_score:
                        best_match = key
                        best_score = score
        
        if best_match and best_score > 0.5:  # Only return if score is reasonably high
            return best_match, db_dict[best_match], best_score
        return None, None, 0
    
    def translate(self, text, source_lang, target_lang):
        """Translate text from source language to target language with improved search"""
        if not text:
            return ''
        
        # Normalize input
        text_normalized = self._normalize_text(text, source_lang)
        source_lang = source_lang.lower()
        target_lang = target_lang.lower()
        
        # If source and target are the same, return original text
        if source_lang == target_lang:
            return text.strip()
        
        # ========== STEP 1: Try exact match first ==========
        if source_lang in self.translation_db:
            # For English, search case-insensitively
            if source_lang == 'english':
                if text_normalized in self.translation_db[source_lang]:
                    translation_entry = self.translation_db[source_lang][text_normalized]
                    if target_lang in translation_entry:
                        result = translation_entry[target_lang]
                        if result and result.strip():  # Only return if result is not empty
                            try:
                                print(f"[EXACT MATCH] {source_lang}->{target_lang}: {repr(text_normalized)}")
                            except:
                                pass
                            return result
            else:
                # For Bodo/Mizo, search with exact match first
                # Try exact match (case-sensitive for Devanagari/Latin)
                if text_normalized in self.translation_db[source_lang]:
                    translation_entry = self.translation_db[source_lang][text_normalized]
                    if target_lang in translation_entry:
                        result = translation_entry[target_lang]
                        if result and result.strip():  # Only return if result is not empty
                            try:
                                print(f"[EXACT MATCH] {source_lang}->{target_lang}")
                            except:
                                pass
                            return result
                
                # Try case-insensitive match for Bodo/Mizo as fallback
                text_lower = text.strip().lower()
                for key in self.translation_db[source_lang]:
                    if key.lower() == text_lower:
                        translation_entry = self.translation_db[source_lang][key]
                        if target_lang in translation_entry:
                            result = translation_entry[target_lang]
                            if result and result.strip():  # Only return if result is not empty
                                try:
                                    print(f"[CASE-INSENSITIVE MATCH] {source_lang}->{target_lang}")
                                except:
                                    pass
                                return result
        
        # ========== STEP 2: Try transitive translation (source -> English -> target) ==========
        if source_lang != 'english' and source_lang in self.translation_db:
            if text_normalized in self.translation_db[source_lang]:
                translation_entry = self.translation_db[source_lang][text_normalized]
                if 'english' in translation_entry and translation_entry['english']:
                    english_text = translation_entry['english']
                    # Now translate English to target
                    english_lower = self._normalize_text(english_text, 'english')
                    if english_lower in self.translation_db['english']:
                        english_entry = self.translation_db['english'][english_lower]
                        if target_lang in english_entry:
                            result = english_entry[target_lang]
                            if result and result.strip():  # Only return if result is not empty
                                try:
                                    print(f"[TRANSITIVE] {source_lang}->{target_lang} via english")
                                except:
                                    pass
                                return result
        
        # ========== STEP 3: Try partial/fuzzy match ==========
        if source_lang in self.translation_db:
            match_key, match_entry, score = self._partial_match_search(
                text_normalized, 
                self.translation_db[source_lang], 
                source_lang
            )
            if match_key and match_entry and score > 0.5:
                # Found a partial match
                if source_lang == 'english':
                    if target_lang in match_entry:
                        result = match_entry[target_lang]
                        if result and result.strip():  # Only return if result is not empty
                            try:
                                print(f"[PARTIAL MATCH] {source_lang}->{target_lang} (score: {score:.2f})")
                            except:
                                pass
                            return result
                else:
                    # For Bodo/Mizo, try transitive through English
                    if 'english' in match_entry and match_entry['english']:
                        english_text = match_entry['english']
                        english_lower = self._normalize_text(english_text, 'english')
                        if english_lower in self.translation_db['english']:
                            english_entry = self.translation_db['english'][english_lower]
                            if target_lang in english_entry:
                                result = english_entry[target_lang]
                                if result and result.strip():  # Only return if result is not empty
                                    try:
                                        print(f"[PARTIAL TRANSITIVE] {source_lang}->{target_lang} (score: {score:.2f})")
                                    except:
                                        pass
                                    return result
        
        # ========== STEP 4: Word-by-word translation for English only ==========
        if source_lang == 'english':
            # Fallback: Try word-by-word translation
            words = text_normalized.split()
            translated_words = []
            found_translations = 0
            
            for word in words:
                # Remove punctuation for lookup
                clean_word = word.strip('.,!?;:\'"')
                
                if clean_word and clean_word in self.translation_db[source_lang]:
                    translation_entry = self.translation_db[source_lang][clean_word]
                    if target_lang in translation_entry:
                        trans_word = translation_entry[target_lang]
                        if trans_word and trans_word.strip():  # Only use non-empty translations
                            translated_words.append(trans_word)
                            found_translations += 1
                        else:
                            translated_words.append(word)
                    else:
                        translated_words.append(word)
                else:
                    translated_words.append(word)
            
            # If at least one word was translated, return the result
            if found_translations > 0:
                translated_text = ' '.join(translated_words)
                try:
                    print(f"[WORD-BY-WORD] {source_lang}->{target_lang}: {found_translations}/{len(words)} words")
                except:
                    pass
                return translated_text
        
        # ========== STEP 5: Not found ==========
        try:
            print(f"[NOT FOUND] {source_lang}->{target_lang}: '{text}'")
        except:
            pass
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
