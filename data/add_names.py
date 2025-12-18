#!/usr/bin/env python3
"""
Add names to classroom_dataset_complete.csv
"""

import csv

# Male names
MALE_NAMES = [
    "Aarav", "Advait", "Akhil", "Amit", "Amar", "Anand", "Aniket", "Arjun", "Aryan", "Ashok",
    "Bala", "Bharath", "Bhavesh", "Charan", "Chaitanya", "Daksh", "Darshan", "Deepak", "Dev", "Dhanush",
    "Dinesh", "Durga Prasad", "Gaurav", "Ganesh", "Girish", "Govind", "Harish", "Harsha", "Hemant", "Ishan",
    "Jatin", "Jay", "Jeevan", "Jitendra", "Kamal", "Karan", "Karthik", "Keshav", "Kiran", "Krishna",
    "Lakshman", "Lohith", "Mahesh", "Manoj", "Mayur", "Mohan", "Mukesh", "Naveen", "Narendra", "Nikhil",
    "Niranjan", "Omkar", "Pankaj", "Pavan", "Pradeep", "Prakash", "Pranav", "Pratap", "Prem", "Rahul",
    "Raj", "Raja", "Rajesh", "Rakesh", "Ram", "Ravi", "Rohit", "Sachin", "Sagar", "Sai",
    "Sandeep", "Santhosh", "Sarath", "Satish", "Saurabh", "Shankar", "Shashank", "Shiva", "Siddharth", "Sooraj",
    "Subhash", "Sudeep", "Suhas", "Suraj", "Surya", "Tarun", "Teja", "Uday", "Umesh", "Varun",
    "Venkatesh", "Vignesh", "Vikas", "Vijay", "Vimal", "Vinay", "Vinit", "Vishal", "Vivek", "Yogesh"
]

# Female names
FEMALE_NAMES = [
    "Aadhya", "Aarohi", "Aarti", "Aishwarya", "Akshara", "Ananya", "Anjali", "Anitha", "Anushka", "Aparna",
    "Archana", "Arpita", "Bhavani", "Bhuvana", "Charitha", "Chandana", "Deepika", "Deeksha", "Divya", "Durga",
    "Eesha", "Gauri", "Gayathri", "Greeshma", "Harini", "Hema", "Indira", "Ira", "Ishika", "Jahnavi",
    "Janani", "Jaya", "Jayashree", "Jyothi", "Kajal", "Kalyani", "Kamala", "Kamalini", "Kavitha", "Keerthi",
    "Kritika", "Lakshmi", "Lavanya", "Leela", "Madhavi", "Madhu", "Mahima", "Malini", "Manisha", "Meena",
    "Meenakshi", "Mounika", "Mythri", "Nalini", "Namitha", "Nandini", "Neelima", "Neha", "Niharika", "Nikki",
    "Pallavi", "Pooja", "Poorna", "Pranitha", "Prathyusha", "Preethi", "Priya", "Radha", "Rajani", "Ramya",
    "Rekha", "Renuka", "Renu", "Rhea", "Rithika", "Sahana", "Sai Lakshmi", "Sandhya", "Sanjana", "Sapna",
    "Saranya", "Sarita", "Seema", "Shalini", "Shanthi", "Sharmila", "Sheetal", "Shilpa", "Shravani", "Shruthi",
    "Shweta", "Sindhu", "Siri", "Sita", "Smitha", "Sneha", "Soumya", "Sravani", "Sridevi", "Srinidhi",
    "Subhalakshmi", "Sujatha", "Suma", "Sunitha", "Surekha", "Sushma", "Swathi", "Tanvi", "Uma", "Urmila",
    "Vaishnavi", "Varsha", "Vasudha", "Vedika", "Vidya", "Vijaya", "Yamini", "Yashoda"
]

# Transliteration helper (simple phonetic to Devanagari)
def transliterate_to_devanagari(name):
    """Simple transliteration of common Indian names to Devanagari."""
    transliterations = {
        "Aarav": "आरव", "Advait": "अद्वैत", "Akhil": "अखिल", "Amit": "अमित", "Amar": "अमर",
        "Anand": "आनंद", "Aniket": "अनिकेत", "Arjun": "अर्जुन", "Aryan": "आर्यन", "Ashok": "अशोक",
        "Bala": "बाला", "Bharath": "भरत", "Bhavesh": "भवेश", "Charan": "चरण", "Chaitanya": "चैतन्य",
        "Daksh": "दक्ष", "Darshan": "दर्शन", "Deepak": "दीपक", "Dev": "देव", "Dhanush": "धनुष",
        "Dinesh": "दिनेश", "Durga Prasad": "दुर्गा प्रसाद", "Gaurav": "गौरव", "Ganesh": "गणेश",
        "Girish": "गिरीश", "Govind": "गोविंद", "Harish": "हरीश", "Harsha": "हर्ष", "Hemant": "हेमंत",
        "Ishan": "ईशान", "Jatin": "जतिन", "Jay": "जय", "Jeevan": "जीवन", "Jitendra": "जितेंद्र",
        "Kamal": "कमल", "Karan": "करण", "Karthik": "कार्तिक", "Keshav": "केशव", "Kiran": "किरण",
        "Krishna": "कृष्ण", "Lakshman": "लक्ष्मण", "Lohith": "लोहित", "Mahesh": "महेश", "Manoj": "मनोज",
        "Mayur": "मयूर", "Mohan": "मोहन", "Mukesh": "मुकेश", "Naveen": "नवीन", "Narendra": "नरेंद्र",
        "Nikhil": "निखिल", "Niranjan": "निरंजन", "Omkar": "ओमकार", "Pankaj": "पंकज", "Pavan": "पवन",
        "Pradeep": "प्रदीप", "Prakash": "प्रकाश", "Pranav": "प्रणव", "Pratap": "प्रताप", "Prem": "प्रेम",
        "Rahul": "राहुल", "Raj": "राज", "Raja": "राजा", "Rajesh": "राजेश", "Rakesh": "राकेश",
        "Ram": "राम", "Ravi": "रवि", "Rohit": "रोहित", "Sachin": "सचिन", "Sagar": "सागर",
        "Sai": "साई", "Sandeep": "संदीप", "Santhosh": "संतोष", "Sarath": "सारथ", "Satish": "सतीश",
        "Saurabh": "सौरभ", "Shankar": "शंकर", "Shashank": "शशांक", "Shiva": "शिव", "Siddharth": "सिद्धार्थ",
        "Sooraj": "सूरज", "Subhash": "सुभाष", "Sudeep": "सुदीप", "Suhas": "सुहास", "Suraj": "सुराज",
        "Surya": "सूर्य", "Tarun": "तारुण", "Teja": "तेज", "Uday": "उदय", "Umesh": "उमेश",
        "Varun": "वरुण", "Venkatesh": "वेंकटेश", "Vignesh": "विग्नेश", "Vikas": "विकास", "Vijay": "विजय",
        "Vimal": "विमल", "Vinay": "विनय", "Vinit": "विनीत", "Vishal": "विशाल", "Vivek": "विवेक", "Yogesh": "योगेश",
        
        "Aadhya": "आध्या", "Aarohi": "आरोही", "Aarti": "आरती", "Aishwarya": "ऐश्वर्या", "Akshara": "अक्षरा",
        "Ananya": "अनन्या", "Anjali": "अंजली", "Anitha": "अनिता", "Anushka": "अनुष्का", "Aparna": "अपर्णा",
        "Archana": "अर्चना", "Arpita": "अर्पिता", "Bhavani": "भवानी", "Bhuvana": "भुवना", "Charitha": "चरिता",
        "Chandana": "चंदना", "Deepika": "दीपिका", "Deeksha": "दीक्षा", "Divya": "दिव्य", "Durga": "दुर्गा",
        "Eesha": "ईशा", "Gauri": "गौरी", "Gayathri": "गायत्री", "Greeshma": "ग्रीष्मा", "Harini": "हरिणी",
        "Hema": "हेमा", "Indira": "इंदिरा", "Ira": "इरा", "Ishika": "ईशिका", "Jahnavi": "जाह्नवी",
        "Janani": "जननी", "Jaya": "जया", "Jayashree": "जयश्री", "Jyothi": "ज्योति", "Kajal": "काजल",
        "Kalyani": "कल्याणी", "Kamala": "कमला", "Kamalini": "कामलिनी", "Kavitha": "कविता", "Keerthi": "कीर्ति",
        "Kritika": "कृतिका", "Lakshmi": "लक्ष्मी", "Lavanya": "लवण्य", "Leela": "लीला", "Madhavi": "मधावी",
        "Madhu": "मधु", "Mahima": "महिमा", "Malini": "मालिनी", "Manisha": "मनीषा", "Meena": "मीना",
        "Meenakshi": "मीनाक्षी", "Mounika": "मौनिका", "Mythri": "मित्री", "Nalini": "नलिनी", "Namitha": "नमिता",
        "Nandini": "नंदिनी", "Neelima": "नीलिमा", "Neha": "नेहा", "Niharika": "निहारिका", "Nikki": "निक्की",
        "Pallavi": "पल्लवी", "Pooja": "पूजा", "Poorna": "पूर्णा", "Pranitha": "प्रणिता", "Prathyusha": "प्रत्यूषा",
        "Preethi": "प्रीति", "Priya": "प्रिया", "Radha": "राधा", "Rajani": "रजनी", "Ramya": "रम्या",
        "Rekha": "रेखा", "Renuka": "रेणुका", "Renu": "रेणु", "Rhea": "रिया", "Rithika": "रितिका",
        "Sahana": "सहना", "Sai Lakshmi": "साई लक्ष्मी", "Sandhya": "संध्या", "Sanjana": "संजना", "Sapna": "सपना",
        "Saranya": "सारण्य", "Sarita": "सरिता", "Seema": "सीमा", "Shalini": "शालिनी", "Shanthi": "शांति",
        "Sharmila": "शर्मिला", "Sheetal": "शीतल", "Shilpa": "शिल्पा", "Shravani": "श्रवणी", "Shruthi": "श्रुति",
        "Shweta": "श्वेता", "Sindhu": "सिंधु", "Siri": "सीरी", "Sita": "सीता", "Smitha": "स्मिता",
        "Sneha": "स्नेहा", "Soumya": "सौम्य", "Sravani": "श्रवणी", "Sridevi": "श्रीदेवी", "Srinidhi": "श्रीनिधि",
        "Subhalakshmi": "सुभलक्ष्मी", "Sujatha": "सुजाता", "Suma": "सुमा", "Sunitha": "सुनिता", "Surekha": "सुरेखा",
        "Sushma": "सुषमा", "Swathi": "स्वाति", "Tanvi": "तन्वी", "Uma": "उमा", "Urmila": "उर्मिला",
        "Vaishnavi": "वैष्णवी", "Varsha": "वर्षा", "Vasudha": "वसुंधा", "Vedika": "वेदिका", "Vidya": "विद्या",
        "Vijaya": "विजया", "Yamini": "यामिनी", "Yashoda": "यशोदा"
    }
    return transliterations.get(name, name)

def get_next_id(csv_path):
    """Get the next available ID from the dataset."""
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) > 1:
                last_line = lines[-1].strip()
                if last_line:
                    last_id = int(last_line.split(',')[0])
                    return last_id + 1
    except Exception as e:
        print(f"Warning: {e}")
    return 1

def main():
    csv_path = r'd:\classroom-assistant\data\classroom_dataset_complete.csv'
    
    next_id = get_next_id(csv_path)
    
    all_names = MALE_NAMES + FEMALE_NAMES
    print(f"Adding {len(all_names)} names to dataset...")
    print(f"Starting ID: {next_id:04d}")
    
    # Append to CSV
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        current_id = next_id
        for name in all_names:
            bodo_trans = transliterate_to_devanagari(name)
            writer.writerow([f"{current_id:04d}", name, bodo_trans, name, "Person Names"])
            current_id += 1
    
    final_id = current_id - 1
    print(f"\n✅ Successfully added {len(all_names)} names!")
    print(f"Final ID: {final_id:04d}")
    print(f"Total entries in dataset: {final_id}")

if __name__ == '__main__':
    main()
