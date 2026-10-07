import streamlit as st
import pandas as pd
import joblib
import numpy as np
import json
import datetime
import hashlib
import os
from fpdf import FPDF

# --- USER AUTHENTICATION SYSTEM (Offline) ---
USER_DB_FILE = "users.json"

def load_users():
    if not os.path.exists(USER_DB_FILE):
        return {}
    try:
        with open(USER_DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_hash, input_password):
    return stored_hash == hashlib.sha256(input_password.encode()).hexdigest()

# --- Bilingual UI Text ---
ui_strings = {
    'en': {
        'page_title': "GramHealth AI (v2.0) - Offline Mode",
        'header_title': "🩺 GramHealth AI",
        'header_subtitle': "Your AI-powered preliminary health screening assistant.",
        'col1_header': "Tell us about you",
        'col1_symptoms': "What are your symptoms?",
        'col2_header': "Your Preliminary Analysis",
        'lang_select_label': "Select Language",
        'age_label': "Age",
        'gender_label': "Gender",
        'gender_options': ["Male", "Female", "Other"],
        'symptom_select_label': "Search & Select Symptoms",
        'symptom_input_label': "Or type here (comma-separated)",
        'predict_button': "Get Analysis",
        'prediction_header': "Primary Possibility",
        'first_aid_header': "Recommended First Aid",
        'doctor_header': "When to See a Doctor",
        'diff_diag_header': "Other Possibilities",
        'symptom_note': "Search symptoms in English or Tamil.",
        'disclaimer_title': "⚠️ Medical Disclaimer",
        'disclaimer_text': "This tool is for informational purposes only. Consult a doctor for medical advice.",
        'download_label': "📥 Download Report (PDF)",
        'pdf_note': "(Report in English)"
    },
    'ta': {
        'page_title': "கிராம்ஹெல்த் AI (v2.0) - ஆஃப்லைன்",
        'header_title': "🩺 கிராம்ஹெல்த் AI",
        'header_subtitle': "உங்கள் செயற்கை நுண்ணறிவு சுகாதார உதவியாளர்.",
        'col1_header': "உங்களைப் பற்றி சொல்லுங்கள்",
        'col1_symptoms': "உங்கள் அறிகுறிகள் என்ன?",
        'col2_header': "உங்கள் முதன்மை ஆய்வு",
        'lang_select_label': "மொழியைத் தேர்ந்தெடுக்கவும்",
        'age_label': "வயது",
        'gender_label': "பாலினம்",
        'gender_options': ["ஆண்", "பெண்", "மற்றவை"],
        'symptom_select_label': "அறிகுறிகளைத் தேடுங்கள்",
        'symptom_input_label': "அல்லது இங்கே தட்டச்சு செய்யவும்",
        'predict_button': "ஆய்வு செய்யவும்",
        'prediction_header': "முதன்மை கணிப்பு",
        'first_aid_header': "பரிந்துரைக்கப்பட்ட முதலுதவி",
        'doctor_header': "மருத்துவரை எப்போது அணுக வேண்டும்",
        'diff_diag_header': "மற்ற சாத்தியக்கூறுகள்",
        'symptom_note': "நீங்கள் ஆங்கிலம் அல்லது தமிழில் தேடலாம்.",
        'disclaimer_title': "⚠️ மருத்துவ மறுப்பு",
        'disclaimer_text': "இது தகவல் நோக்கங்களுக்காக மட்டுமே. மருத்துவ ஆலோசனைக்கு மருத்துவரை அணுகவும்.",
        'download_label': "📥 அறிக்கையைப் பதிவிறக்கவும் (PDF)",
        'pdf_note': "(அறிக்கை ஆங்கிலத்தில் இருக்கும்)"
    }
}

def comma_tokenizer(text):
    if not isinstance(text, str):
        return []
    text = text.lower() 
    return [symptom.strip() for symptom in text.split(',') if symptom.strip()]

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'GramHealth AI - Patient Report', 0, 1, 'C')
        self.ln(5)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf_report(disease_en, symptoms, advice_list_en, doctor_advice_en, age, gender):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Patient Details:", 0, 1)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1)
    pdf.cell(0, 8, f"Age: {age} | Gender: {gender}", 0, 1)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Reported Symptoms:", 0, 1)
    pdf.set_font("Arial", size=12)
    safe_symptoms = symptoms.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 8, safe_symptoms)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    safe_disease = disease_en.encode('latin-1', 'ignore').decode('latin-1')
    pdf.cell(0, 10, f"Predicted Condition: {safe_disease}", 0, 1)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Recommended First Aid:", 0, 1)
    pdf.set_font("Arial", size=12)
    for item in advice_list_en:
        safe_text = item.encode('latin-1', 'ignore').decode('latin-1')
        pdf.multi_cell(0, 8, f"- {safe_text}")
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(0, 10, "When to see a Doctor:", 0, 1)
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0, 0, 0)
    safe_doc_advice = doctor_advice_en.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 8, safe_doc_advice)
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(0, 5, "Disclaimer: generated by AI. Consult a doctor.")
    return pdf.output(dest='S').encode('latin-1')

st.set_page_config(page_title="GramHealth AI", page_icon="🩺", layout="wide")

@st.cache_data
def load_resources():
    try:
        model = joblib.load('gramhealth_ai_model.joblib')
        df = pd.read_csv('processed_dataset.csv')
        with open('knowledge_base.json', 'r', encoding='utf-8') as f:
            knowledge_base = json.load(f)
        try:
            with open('symptom.json', 'r', encoding='utf-8') as f:
                symptom_translations = json.load(f)
        except FileNotFoundError:
            symptom_translations = {} 
        return model, df, knowledge_base, symptom_translations
    except Exception as e:
        st.error(f"Error loading resources: {e}")
        st.stop()

def main():
    # Initialize Authentication State
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""

    # --- AUTHENTICATION LOGIC ---
    if not st.session_state.logged_in:
        st.title("🩺 GramHealth AI - Login")
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        # LOGIN TAB
        with tab1:
            st.subheader("Welcome Back")
            login_user = st.text_input("Username", key="login_user")
            login_pass = st.text_input("Password", type="password", key="login_pass")
            
            if st.button("Login", type="primary"):
                users = load_users()
                if login_user in users and verify_password(users[login_user], login_pass):
                    st.session_state.logged_in = True
                    st.session_state.username = login_user
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid Username or Password")

        # SIGN UP TAB
        with tab2:
            st.subheader("Create New Account")
            new_user = st.text_input("New Username", key="new_user")
            new_pass = st.text_input("New Password", type="password", key="new_pass")
            confirm_pass = st.text_input("Confirm Password", type="password", key="confirm_pass")
            
            if st.button("Sign Up"):
                if new_pass != confirm_pass:
                    st.error("Passwords do not match!")
                elif new_user == "":
                    st.error("Username cannot be empty!")
                else:
                    users = load_users()
                    if new_user in users:
                        st.error("Username already exists!")
                    else:
                        users[new_user] = hash_password(new_pass)
                        save_users(users)
                        st.success("Account created! Please go to Login tab.")

        return # Stop execution here if not logged in

    # --- MAIN APP LOGIC (Only runs if logged in) ---
    
    # Logout Button in Sidebar
    st.sidebar.title(f"Welcome, {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    # Load Resources only after login
    model, df, kb, symptom_translations = load_resources() 

    # App States
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False
    if 'symptoms_string' not in st.session_state:
        st.session_state.symptoms_string = ""

    # Language Logic
    lang_options = {"English": "en", "தமிழ் (Tamil)": "ta"}
    st.sidebar.divider()
    st.sidebar.title("Settings / அமைப்புகள்")
    lang_choice_label = st.sidebar.radio("Language / மொழி", options=lang_options.keys())
    lang_code = lang_options[lang_choice_label]
    ui = ui_strings[lang_code]

    # --- HEADER ---
    st.title(ui['header_title'])
    st.markdown(f"**{ui['header_subtitle']}**")
    with st.expander(ui['disclaimer_title'], expanded=False):
        st.warning(ui['disclaimer_text'])
    st.divider()

    # --- TWO COLUMN LAYOUT ---
    col1, col2 = st.columns([1, 1], gap="large")

    # --- LEFT COLUMN: INPUTS ---
    with col1:
        st.header(ui['col1_header'])
        
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input(ui['age_label'], min_value=1, max_value=120, value=25)
        with c2:
            gender = st.radio(ui['gender_label'], options=ui['gender_options'], horizontal=True)
        
        st.markdown("---")
        st.header(ui['col1_symptoms'])
        st.info(ui['symptom_note'])

        # Symptom Logic
        def get_all_symptoms(_df):
            all_symptoms = set()
            for s_list in _df['Symptoms']:
                tokens = comma_tokenizer(s_list)
                for t in tokens:
                    if t and t != 'nan' and len(t) > 1:
                        all_symptoms.add(t)
            return sorted(list(all_symptoms))

        all_symptoms_en = get_all_symptoms(df)
        
        def format_symptom(option):
            translation = symptom_translations.get(option)
            if translation: return f"{option} ({translation})"
            return option

        selected_symptoms = st.multiselect(
            ui['symptom_select_label'], 
            options=all_symptoms_en, 
            format_func=format_symptom
        )
        text_input = st.text_input(ui['symptom_input_label'])

        current_symptoms = ""
        if selected_symptoms:
            current_symptoms = ", ".join(selected_symptoms)
        if text_input:
            if current_symptoms: current_symptoms += ", " + text_input
            else: current_symptoms = text_input

        if st.button(ui['predict_button'], type="primary", use_container_width=True):
            if not current_symptoms:
                st.error("Please select at least one symptom.")
            else:
                st.session_state.symptoms_string = current_symptoms
                st.session_state.show_results = True

    # --- RIGHT COLUMN: RESULTS ---
    with col2:
        if st.session_state.show_results:
            st.header(ui['col2_header'])
            try:
                symptoms_final = st.session_state.symptoms_string
                probabilities = model.predict_proba([symptoms_final])[0]
                
                top_3_indices = np.argsort(probabilities)[::-1][:3]
                top_3_diseases = model.classes_[top_3_indices]
                raw_probs = probabilities[top_3_indices]
                current_sum = np.sum(raw_probs)
                if current_sum > 0:
                    top_3_probs_percent = (raw_probs / current_sum) * 100
                else:
                    top_3_probs_percent = np.array([0.0, 0.0, 0.0])

                final_disease = top_3_diseases[0]
                final_prob_percent = top_3_probs_percent[0]

                if final_disease in kb:
                    details = kb[final_disease]
                    title_local = details.get(f'title_{lang_code}', details.get('title_en', final_disease))
                    title_en = details.get('title_en', final_disease)
                    
                    if title_local.strip() == title_en.strip():
                        display_title = title_local
                    else:
                        display_title = f"{title_local} ({title_en})"
                    
                    st.success(f"### {display_title}")
                    st.progress(int(final_prob_percent))
                    st.caption(f"{ui['prediction_header']} Confidence: **{final_prob_percent:.1f}%**")
                    st.markdown(f"**Description:** {details.get(f'description_{lang_code}', '')}")

                    st.subheader(ui['first_aid_header'])
                    for point in details.get(f'first_aid_{lang_code}', []):
                        st.markdown(f"✅ {point}")

                    st.subheader(ui['doctor_header'])
                    st.warning(f"⚠️ {details.get(f'when_to_see_doctor_{lang_code}', '')}")

                    st.markdown("---")
                    pdf_bytes = create_pdf_report(
                        title_en, symptoms_final, 
                        details.get('first_aid_en', []), 
                        details.get('when_to_see_doctor_en', ""), 
                        age, gender
                    )
                    st.download_button(
                        label=ui['download_label'],
                        data=pdf_bytes, 
                        file_name=f"GramHealth_Report.pdf", 
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.caption(ui['pdf_note'])

                else:
                    st.error(f"No data for {final_disease}")

                st.divider()

                with st.expander(ui['diff_diag_header']):
                    if len(top_3_diseases) > 1:
                        for i in range(1, len(top_3_diseases)):
                            d_name = top_3_diseases[i]
                            d_prob = top_3_probs_percent[i]
                            if d_name in kb:
                                d_det = kb[d_name]
                                d_tit_local = d_det.get(f'title_{lang_code}', d_name)
                                d_tit_en = d_det.get('title_en', d_name)
                                
                                if d_tit_local.strip() == d_tit_en.strip():
                                    d_display = d_tit_local
                                else:
                                    d_display = f"{d_tit_local} ({d_tit_en})"

                                st.write(f"**{d_display}**: {d_prob:.1f}%")
                            else:
                                st.write(f"**{d_name}**: {d_prob:.1f}%")

            except Exception as e:
                st.error(f"Error: {e}")

        else:
            st.info("👈 Please enter your details and symptoms on the left to see the analysis here.")

if __name__ == "__main__":
    main()