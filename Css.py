import streamlit as st
import sqlite3

def style_css():
    # --- CSS Styling ---
    st.markdown("""
    <style>
        :root {
            --primary-dark: #202020;
            --secondary-gray: #8c8c8c;
            --accent-red: #f10000;
            --dark-red-accent: #6c1313;
            --light-gray: #94948c;
            --off-white: #faf5ee;
            --main-background: #dedbd7;
            --sidebar-bg: #000000;
        }

        /* 1. STYLE DU SIDEBAR (CONSERVÉ EXACTEMENT TEL QU'IL ÉTAIT DANS VOTRE CODE INITIAL) */
        [data-testid="stSidebar"] {
            background-color: var(--sidebar-bg) !important;
            color: white !important;
        }
        
        [data-testid="stSidebar"] .st-emotion-cache-16txtl3 {
            padding: 2rem 1rem;
        }
        
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] h4, 
        [data-testid="stSidebar"] h5, 
        [data-testid="stSidebar"] h6,
        [data-testid="stSidebar"] p {
            color: white !important;
        }

        /* Boutons du sidebar - style initial conservé */
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] .stButton > button {
            background-color: transparent !important;
            color: white !important;
            border: none;
            border-radius: 8px;
            padding: 12px 20px;
            text-align: left;
            box-shadow: none;
            transition: background-color 0.2s ease, color 0.2s ease;
            width: 100%;
            font-weight: bold;
            margin: 5px 0;
        }
        
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] .stButton > button:hover {
            background-color: rgba(241, 0, 0, 0.3) !important;
            color: white !important;
        }

        /* 2. STYLE UNIFIÉ POUR TOUS LES AUTRES BOUTONS (COULEURS INVERSÉES) */
        /* Style de base pour tous les boutons HORS sidebar */
        /* Using :not([data-testid="stSidebar"] .stButton) to explicitly exclude sidebar buttons */
        div[data-testid="stVerticalBlock"] .stButton > button:not([data-testid="stSidebar"] .stButton),
        div[data-testid="stHorizontalBlock"] .stButton > button:not([data-testid="stSidebar"] .stButton),
        .stForm button[type="submit"]:not([data-testid="stSidebar"] .stButton),
        .stButton:not([data-testid="stSidebar"] .stButton) > button {
            background-color: var(--primary-dark) !important; /* Inverted: dark background */
            color: var(--accent-red) !important; /* Inverted: red text */
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
            display: inline-flex;
            justify-content: center;
            align-items: center;
            min-width: 120px;
            cursor: pointer;
        }

        /* Effet hover (ajusté pour les couleurs inversées) */
        div[data-testid="stVerticalBlock"] .stButton > button:hover:not([data-testid="stSidebar"] .stButton),
        div[data-testid="stHorizontalBlock"] .stButton > button:hover:not([data-testid="stSidebar"] .stButton),
        .stForm button[type="submit"]:hover:not([data-testid="stSidebar"] .stButton),
        .stButton:not([data-testid="stSidebar"] .stButton) > button:hover {
            background-color: var(--dark-red-accent) !important; /* Adjusted: darker red on hover */
            color: var(--off-white) !important; /* Adjusted: off-white text on hover */
            transform: translateY(-2px);
            box-shadow: 3px 3px 8px rgba(0, 0, 0, 0.3);
        }

        /* Effet clic (pas de changement majeur nécessaire ici) */
        div[data-testid="stVerticalBlock"] .stButton > button:active:not([data-testid="stSidebar"] .stButton),
        div[data-testid="stHorizontalBlock"] .stButton > button:active:not([data-testid="stSidebar"] .stButton),
        .stForm button[type="submit"]:active:not([data-testid="stSidebar"] .stButton),
        .stButton:not([data-testid="stSidebar"] .stButton) > button:active {
            transform: translateY(0);
            box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
        }

        /* Boutons secondaires dans les formulaires (couleurs ajustées) */
        .stForm .stButton:not(:first-child) > button:not([data-testid="stSidebar"] .stButton),
        .stForm button:not([type="submit"]):not([data-testid="stSidebar"] .stButton) {
            background-color: var(--secondary-gray) !important;
            color: var(--primary-dark) !important; /* Adjusted: dark text on gray background */
        }

        .stForm .stButton:not(:first-child) > button:hover:not([data-testid="stSidebar"] .stButton),
        .stForm button:not([type="submit"]):hover:not([data-testid="stSidebar"] .stButton) {
            background-color: var(--light-gray) !important;
            color: var(--primary-dark) !important; /* Adjusted: dark text on lighter gray hover */
        }

        /* 3. STYLE DES IMAGES EN CERCLES (CONSERVE) */
        .profile-picture-circle {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            object-fit: cover;
            border: 3px solid var(--accent-red);
            background-color: var(--dark-red-accent);
            padding: 5px;
            margin: 0 auto;
            display: block;
        }
        
        .vehicle-picture-circle {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid var(--accent-red);
            background-color: var(--dark-red-accent);
            padding: 3px;
            margin: 0 auto;
        }

        /* 4. STYLE GENERAL DE L'APPLICATION */
        html, body, [data-testid="stAppViewContainer"] {
            font-family: "Inter", sans-serif;
            background-color: var(--main-background);
            color: var(--primary-dark);
        }

        h1, h2, h3, h4, h5, h6 {
            color: var(--accent-red);
            font-weight: bold;
        }

        /* Style des champs de formulaire */
        /* Labels for form fields in the main content area */
        .stTextInput > label,
        .stDateInput > label,
        .stTimeInput > label,
        .stNumberInput > label,
        .stSelectbox > label, 
        .stRadio > label, 
        .stCheckbox > label {
            color: var(--primary-dark); /* Ensure main content labels are dark */
            font-weight: bold;
        }

        /* Styling for the actual input areas (text, date, time, number, selectbox, radio, checkbox containers) */
        .stTextInput > div > div > input,
        .stDateInput > div > input,
        .stTimeInput > div > input,
        .stNumberInput > div > input,
        .stSelectbox > div > div, /* Target selectbox display area */
        .stRadio > div, /* Target radio button group container */
        .stCheckbox > div { /* Target checkbox group container */
            background-color: var(--off-white); /* Lighter background for actual input areas */
            color: var(--primary-dark);
            border: 1px solid var(--secondary-gray);
            border-radius: 8px;
            padding: 10px;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
            box-sizing: border-box; /* Include padding and border in the element's total width and height */
        }

        /* Specific padding for direct input fields */
        .stTextInput > div > div > input,
        .stDateInput > div > input,
        .stTimeInput > div > input,
        .stNumberInput > div > input {
            padding: 10px; /* Ensure padding is applied directly to input fields */
            width: 100%;
        }

        /* File uploader button styling (to match other main buttons) */
        .stFileUploader > div > div > button {
             background-color: var(--primary-dark) !important;
             color: var(--accent-red) !important;
             border: none;
             box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
        }
        .stFileUploader > div > div > button:hover {
             background-color: var(--dark-red-accent) !important;
             color: var(--off-white) !important;
             transform: translateY(-2px);
             box-shadow: 3px 3px 8px rgba(0, 0, 0, 0.3);
        }

        /* Style des cartes */
        .info-card {
            background-color: var(--light-gray);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 5px solid var(--accent-red);
        }
        
        .vehicle-card {
            background-color: var(--off-white);
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
            border: 1px solid var(--secondary-gray);
            box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.1);
            height: 100%;
            display: flex;
            flex-direction: column;
        }
    </style>
    """, unsafe_allow_html=True)
