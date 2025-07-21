import streamlit as st
import sqlite3
import bcrypt
import datetime
from datetime import date
from PIL import Image
import os
import base64

# --- Configuration des dossiers pour les images (Doit être cohérent avec Database_Fahrten.py) ---
UPLOAD_DIR = "uploads"
PROFILE_PICTURES_DIR = os.path.join(UPLOAD_DIR, "profile_pictures")
VEHICLE_PICTURES_DIR = os.path.join(UPLOAD_DIR, "vehicle_pictures")

# Assurez-vous que les dossiers existent
os.makedirs(PROFILE_PICTURES_DIR, exist_ok=True)
os.makedirs(VEHICLE_PICTURES_DIR, exist_ok=True)

# --- Importations des modules locaux ---
# Assurez-vous que toutes les fonctions nécessaires sont importées
from Database_Fahrten import (
    setup_db, add_vehicul_db, save_vehicle_image, save_profile_picture, save_image,
    update_user_profile_picture, update_vehicul_pictures, delete_image, display_image,
    register_user_db, get_user_by_username_db, update_user_profile_db,
    add_ride_db, get_rides_db, delete_ride_db, update_ride_db,
    book_ride_db, get_user_bookings_db, get_user_vehiculs_db
)
from Utils_Fahrten import display_logo, hash_password, verify_password, translate, get_base64_icon
from Rides import show_display_rides, show_my_rides, show_offer_ride, edit_ride # Assuming Rides.py exists and contains these

# --- Helper Functions for UI ---

def display_app_header(page_title):
    """Displays the application header with logo and title."""
    col1, col2 = st.columns([0.1, 2])
    with col1:
        display_logo(os.path.join("Images", "Logo_MitFahrn.PNG"), width=100)
    with col2:
        st.markdown(f"""
        <h1 style='color: var(--accent-red); font-weight: bold; border-bottom: 2px solid var(--secondary-gray); padding-bottom: 10px;'>
            {translate(page_title)}
        </h1>
        """, unsafe_allow_html=True)
    st.markdown("---")

def styled_subheader(text):
    """Displays a styled subheader."""
    st.markdown(f"""
    <h2 style='color: var(--accent-red); font-weight: bold; margin-top: 20px;'>
        {translate(text)}
    </h2>
    """, unsafe_allow_html=True)

def display_full_path_image(image_relative_path, caption, width=None):
    """
    Displays an image from a path relative to UPLOAD_DIR.
    This replaces the previous display_vehicle_image and handles profile pictures too.
    """
    if image_relative_path:
        full_path = os.path.join(UPLOAD_DIR, image_relative_path)
        if os.path.exists(full_path):
            try:
                image = Image.open(full_path)
                st.image(image, caption=caption, width=width)
            except Exception as e:
                st.warning(f"{translate('Impossible de charger l\'image')} {os.path.basename(full_path)}: {e}")
        else:
            st.info(f"{translate('Image non trouvée pour')} {caption} ({image_relative_path}).")
    else:
        st.info(f"{translate('Pas de chemin d\'image fourni pour')} {caption}.")


# --- Main Application Logic ---

def main():
    """Main function to run the Streamlit application."""
    icon_base64 = get_base64_icon(os.path.join("Images", "Logo_MitFahrn.ico"))
    if icon_base64:
        st.set_page_config(
            layout="wide",
            page_title=translate("Gestion des trajets Priminsberg"),
            page_icon=f"data:image/x-icon;base64,{icon_base64}",
            initial_sidebar_state="expanded"
        )
    else:
        st.set_page_config(
            layout="wide",
            page_title=translate("Gestion des trajets Priminsberg"),
            initial_sidebar_state="expanded"
        )

    setup_db() # Ensure database is set up

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
        }

        html, body, [data-testid="stAppViewContainer"] {
            font-family: "Inter", sans-serif;
            background-color: var(--main-background);
            color: var(--primary-dark);
        }

        h1, h2, h3, h4, h5, h6 {
            color: var(--accent-red);
            font-weight: bold;
        }

        [data-testid="stSidebar"] {
            background-color: var(--primary-dark);
            color: var(--off-white);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 3px 0px 10px rgba(0, 0, 0, 0.3);
        }

        [data-testid="stSidebar"] .st-emotion-cache-1jm50x5 {
            display: none;
        }

        [data-testid="stSidebar"] .st-emotion-cache-10o4u29 {
            color: var(--off-white);
            font-weight: bold;
        }

        .stButton > button {
            background-color: var(--accent-red);
            color: var(--off-white);
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            transition: background-color 0.3s ease, transform 0.2s ease;
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
        }
        .stButton > button:hover {
            background-color: var(--dark-red-accent);
            transform: translateY(-2px);
        }
        .stButton > button:active {
            background-color: var(--dark-red-accent);
            transform: translateY(0);
            box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
        }

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] .stButton {
            margin-bottom: 5px;
        }

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] .stButton > button {
            background-color: transparent;
            color: var(--off-white);
            border: none;
            border-radius: 0;
            padding: 12px 20px;
            text-align: left;
            box-shadow: none;
            transition: background-color 0.2s ease, color 0.2s ease;
            width: 100%;
            font-weight: bold;
        }

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] .stButton > button:hover {
            background-color: rgba(241, 0, 0, 0.2);
            color: var(--accent-red);
            transform: none;
        }

        .stTextInput > div > div > input,
        .stDateInput > div > input,
        .stTimeInput > div > input,
        .stNumberInput > div > input,
        .stFileUploader > div > div > button { /* Apply to file uploader button */
            background-color: var(--light-gray);
            color: var(--primary-dark);
            border: 1px solid var(--secondary-gray);
            border-radius: 8px;
            padding: 10px;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
            font-weight: bold;
        }
        .stTextInput > div > div > input:focus,
        .stDateInput > div > input:focus,
        .stTimeInput > div > input:focus,
        .stNumberInput > div > input:focus {
            border-color: var(--accent-red);
            box-shadow: 0 0 0 2px rgba(241, 0, 0, 0.2);
            outline: none;
        }

        .stTextInput > label,
        .stDateInput > label,
        .stTimeInput > label,
        .stNumberInput > label,
        .stSelectbox > label,
        .stFileUploader > label { /* Apply to file uploader label */
            color: var(--primary-dark);
            font-weight: bold;
            margin-bottom: 5px;
            display: block;
        }

        .stSelectbox > div > div {
            background-color: var(--light-gray);
            color: var(--primary-dark);
            border: 1px solid var(--secondary-gray);
            border-radius: 8px;
            padding: 5px;
            font-weight: bold;
        }
        .stSelectbox > div > div:focus {
            border-color: var(--accent-red);
            box-shadow: 0 0 0 2px rgba(241, 0, 0, 0.2);
            outline: none;
        }
        .stSelectbox .st-emotion-cache-1dp5ifq {
            color: var(--primary-dark);
        }

        .streamlit-expander {
            background-color: var(--main-background);
            border: 1px solid var(--secondary-gray);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.1);
            transition: box-shadow 0.3s ease;
        }
        .streamlit-expander:hover {
            box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.15);
        }
        .streamlit-expanderContent {
            color: var(--primary-dark);
            padding-top: 10px;
            font-weight: bold;
        }
        .streamlit-expanderHeader {
            color: var(--primary-dark);
            font-weight: bold;
            font-size: 1.1em;
        }

        .stAlert {
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            font-weight: bold;
        }
        .stAlert.info {
            background-color: rgba(148, 148, 140, 0.2);
            color: var(--primary-dark);
            border-left: 5px solid var(--secondary-gray);
        }
        .stAlert.success {
            background-color: rgba(241, 0, 0, 0.1);
            color: var(--primary-dark);
            border-left: 5px solid var(--accent-red);
        }
        .stAlert.error {
            background-color: rgba(241, 0, 0, 0.2);
            color: var(--primary-dark);
            border-left: 5px solid var(--accent-red);
        }

        hr {
            border-top: 2px solid var(--secondary-gray);
            margin: 20px 0;
        }

        .st-emotion-cache-1c7y2qn, .st-emotion-cache-ocqkz7 {
            gap: 20px;
        }

        .st-emotion-cache-10q7q0o {
            background-color: var(--main-background);
            border: 1px solid var(--secondary-gray);
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        }

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
        }
        .vehicle-card h4 {
            color: var(--primary-dark);
            font-weight: bold;
            margin-bottom: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- Session State Initialization ---
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'page' not in st.session_state:
        st.session_state.page = "landing"
    if 'menu_selection' not in st.session_state:
        st.session_state.menu_selection = "profile"
    if 'editing_vehicle_id' not in st.session_state: # New state for vehicle editing
        st.session_state.editing_vehicle_id = None

    # --- Conditional Page Rendering (Login/Register/Landing vs. Authenticated User) ---
    if st.session_state.current_user is None:
        if st.session_state.page == "login":
            display_app_header(translate("Connexion"))
            show_login()
        elif st.session_state.page == "register":
            display_app_header(translate("Inscription"))
            show_register()
        else:
            display_app_header(translate("Bienvenue sur Priminsberg Ride"))
            show_landing()
    else:
        # Authenticated User Sidebar Menu
        st.sidebar.markdown(f"""
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: var(--accent-red); font-size: 1.5em; font-weight: bold; 
                        border-bottom: 2px solid var(--dark-red-accent); padding-bottom: 10px;">
                {translate("Bienvenue")}, {st.session_state.current_user[3]}!
            </h2>
        </div>
        """, unsafe_allow_html=True)

        menu_items = [
            (translate("Mon Profil"), "profile"),
            (translate("Fahrten anzeigen"), "display_rides"),
            (translate("Proposer un trajet"), "offer_ride"),
            (translate("Mes trajets"), "my_rides"),
            (translate("Modifier le profil"), "edit_profile") # This is where vehicle management will be
        ]

        for label, key_name in menu_items:
            if st.sidebar.button(label, key=f"menu_{key_name}"):
                st.session_state.menu_selection = key_name
                st.session_state.editing_vehicle_id = None # Reset editing vehicle when changing menu
                st.rerun()

        if st.sidebar.button(translate("Se déconnecter"), key="sidebar_logout_btn"):
            st.session_state.current_user = None
            st.session_state.page = "landing"
            st.session_state.menu_selection = "profile"
            st.session_state.editing_vehicle_id = None # Reset on logout
            st.rerun()

    # --- Authenticated User Main Content Rendering ---
    if st.session_state.current_user is not None:
        if st.session_state.menu_selection == "profile":
            display_app_header(translate("Mon Profil"))
            show_profile()
        elif st.session_state.menu_selection == "display_rides":
            display_app_header(translate("Trajets disponibles"))
            show_display_rides()
        elif st.session_state.menu_selection == "offer_ride":
            display_app_header(translate("Proposer un trajet"))
            show_offer_ride()
        elif st.session_state.menu_selection == "my_rides":
            display_app_header(translate("Mes trajets"))
            show_my_rides()
        elif st.session_state.menu_selection == "edit_profile":
            display_app_header(translate("Modifier le profil"))
            show_edit_profile()

# --- Landing Page ---
def show_landing():
    """Displays the landing page with login/register options."""
    st.markdown(f"""
    <div style='background-color: var(--light-gray); padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h3 style='color: var(--accent-red);'>{translate("Bienvenue sur la plateforme de covoiturage Priminsberg")}</h3>
        <p>{translate("Connectez-vous ou inscrivez-vous pour accéder à toutes les fonctionnalités.")}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button(translate("Se connecter"), key="landing_login_button"):
            st.session_state.page = "login"
            st.rerun()
    with col2:
        if st.button(translate("S'inscrire"), key="landing_register_button"):
            st.session_state.page = "register"
            st.rerun()

# --- Login Page ---
def show_login():
    """Displays the login form."""
    with st.form(key="login_form"):
        username = st.text_input(translate("Nom d'utilisateur"), key="login_username")
        password = st.text_input(translate("Mot de passe"), type="password", key="login_password")

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button(translate("Se connecter")):
                user = get_user_by_username_db(username) # Use the DB function
                if user and verify_password(password, user[2]):
                    st.session_state.current_user = user
                    st.session_state.page = "profile"
                    st.session_state.menu_selection = "profile"
                    st.rerun()
                else:
                    st.error(translate("Échec de la connexion ! Nom d'utilisateur ou mot de passe invalide."))
        with col2:
            if st.form_submit_button(translate("Retour")):
                st.session_state.page = "landing"
                st.rerun()

# --- Register Page ---
def show_register():
    """Displays the user registration form, including profile picture and driving license date."""
    with st.form(key="register_form"):
        username = st.text_input(translate("Nom d'utilisateur"), key="register_username")
        password = st.text_input(translate("Mot de passe"), type="password", key="register_password")
        first_name = st.text_input(translate("Prénom"), key="register_first_name")
        last_name = st.text_input(translate("Nom de famille"), key="register_last_name")
        station = st.text_input(translate("Gare"), help=translate("Votre gare habituelle, ex : 'Hauptbahnhof'"), key="register_station")
        email = st.text_input(translate("Email"), key="register_email")
        phone = st.text_input(translate("Téléphone"), key="register_phone")
        
        # Profile picture upload
        profile_picture_file = st.file_uploader(translate("Photo de profil (Optionnel)"), 
                                               type=["jpg", "jpeg", "png"], 
                                               key="register_profile_pic_uploader")
        
        # Driving license date input
        driving_license_date = st.date_input(translate("Date d'obtention du permis"), 
                                             value=date.today(), 
                                             key="register_license_date")

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button(translate("S'inscrire"))
        with col2:
            if st.form_submit_button(translate("Retour")):
                st.session_state.page = "landing"
                st.rerun()

        if submitted:
            if not all([username, password, first_name, last_name, station, email, phone, driving_license_date]):
                st.error(translate("Veuillez remplir tous les champs obligatoires !"))
            else:
                try:
                    pw_hash = hash_password(password)
                    
                    # Register user initially without profile picture path
                    # The profile_picture argument in register_user_db is for the path, not the file object
                    user_id = register_user_db(username, pw_hash, first_name, last_name, station, email, phone, driving_license_date.strftime('%Y-%m-%d'), None)

                    if user_id:
                        profile_pic_path = None
                        if profile_picture_file is not None:
                            # Save the uploaded profile picture using the new user_id
                            profile_pic_path = save_profile_picture(profile_picture_file, user_id)
                            if profile_pic_path:
                                # Update the user's record with the saved picture path
                                update_user_profile_picture(user_id, profile_pic_path)
                                st.success(translate("Photo de profil téléchargée avec succès !"))
                            else:
                                st.warning(translate("Erreur lors du téléchargement de la photo de profil."))
                        
                        # Fetch the complete user object including the (potentially new) profile picture path
                        st.session_state.current_user = get_user_by_username_db(username)
                        st.success(translate("Inscription terminée !"))
                        st.session_state.page = "profile"
                        st.session_state.menu_selection = "profile"
                        st.rerun()
                    else:
                        st.error(translate("Ce nom d'utilisateur existe déjà !"))
                except Exception as e:
                    st.error(f"{translate('Une erreur est survenue lors de l\'inscription')} : {e}")

# --- Profile Page ---
def show_profile():
    """Displays the user's profile information and registered vehicles."""
    user = st.session_state.current_user
    user_id = user[0]

    st.markdown(f"""
    <div class='info-card'>
        <h3 style='color: var(--accent-red); margin-top: 0;'>{translate("Informations de profil")}</h3>
    """, unsafe_allow_html=True)

    # Display User Profile Picture
    profile_picture_path = user[9] if len(user) > 9 else None # Get profile picture path from user tuple
    display_full_path_image(profile_picture_path, translate("Votre photo de profil"), width=150)

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**{translate('Nom d\'utilisateur')} :** {user[1]}")
        st.write(f"**{translate('Prénom')} :** {user[3]}")
        st.write(f"**{translate('Nom de famille')} :** {user[4]}")
    with col2:
        st.write(f"**{translate('Gare')} :** {user[5]}")
        st.write(f"**{translate('Téléphone')} :** {user[7]}")
        st.write(f"**{translate('Email')} :** {user[6]}")
    
    st.write(f"**{translate('Date d\'obtention du permis')} :** {user[8]}")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    styled_subheader(translate("Mes Véhicules"))

    vehicles = get_user_vehiculs_db(user_id) # Use the DB function

    if vehicles:
        for i, vehicle in enumerate(vehicles):
            vehicle_id, marque, model, date_circulation, pic_inter1, pic_inter2, pic_exter1, pic_exter2 = vehicle
            
            st.markdown(f"""
            <div class='vehicle-card'>
                <h4>{translate("Véhicule")} {i+1}: {marque} {model}</h4>
                <p><strong>{translate('Marque')}:</strong> {marque}</p>
                <p><strong>{translate('Modèle')}:</strong> {model}</p>
                <p><strong>{translate('Date de mise en circulation')}:</strong> {date_circulation}</p>
            """, unsafe_allow_html=True)

            # Display vehicle images
            image_cols = st.columns(4)
            with image_cols[0]:
                display_full_path_image(pic_inter1, translate("Intérieur 1"), width=100)
            with image_cols[1]:
                display_full_path_image(pic_inter2, translate("Intérieur 2"), width=100)
            with image_cols[2]:
                display_full_path_image(pic_exter1, translate("Extérieur 1"), width=100)
            with image_cols[3]:
                display_full_path_image(pic_exter2, translate("Extérieur 2"), width=100)
            
            st.markdown("</div>", unsafe_allow_html=True) # Close vehicle-card div
            st.markdown("---")
    else:
        st.info(translate("Aucun véhicule enregistré pour le moment."))


# --- Vehicle Management Forms (New/Refactored) ---

def show_add_vehicle_form(user_id):
    """Displays a form to add a new vehicle."""
    # The subheader is already outside in show_edit_profile for this expander
    with st.form(key="add_vehicle_form"):
        # Use columns for vehicle details
        col_veh_details1, col_veh_details2 = st.columns(2)
        with col_veh_details1:
            marque = st.text_input(translate("Marque du véhicule"), key="add_veh_marque")
            model = st.text_input(translate("Modèle du véhicule"), key="add_veh_model")
        with col_veh_details2:
            date_mise_en_circulation = st.date_input(translate("Date de mise en circulation"), key="add_veh_date_circulation")
        
        st.markdown("---")
        st.subheader(translate("Images du véhicule (Optionnel)"))
        # Use columns for image uploaders
        col_img_upload1, col_img_upload2 = st.columns(2)
        with col_img_upload1:
            inter1 = st.file_uploader(translate("Image intérieure 1"), type=["jpg", "jpeg", "png"], key="add_veh_inter1")
            inter2 = st.file_uploader(translate("Image intérieure 2"), type=["jpg", "jpeg", "png"], key="add_veh_inter2")
        with col_img_upload2:
            exter1 = st.file_uploader(translate("Image extérieure 1"), type=["jpg", "jpeg", "png"], key="add_veh_exter1")
            exter2 = st.file_uploader(translate("Image extérieure 2"), type=["jpg", "jpeg", "png"], key="add_veh_exter2")
        
        submitted = st.form_submit_button(translate("Ajouter le véhicule"))
        
        if submitted:
            if marque and model and date_mise_en_circulation:
                # Save images first to get their paths
                pictures = {
                    'inter1': save_vehicle_image(inter1, user_id, "inter1") if inter1 else None,
                    'inter2': save_vehicle_image(inter2, user_id, "inter2") if inter2 else None,
                    'exter1': save_vehicle_image(exter1, user_id, "exter1") if exter1 else None,
                    'exter2': save_vehicle_image(exter2, user_id, "exter2") if exter2 else None
                }
                
                # Add the vehicle to the database
                vehicle_id = add_vehicul_db(user_id, marque, model, 
                                             date_mise_en_circulation.strftime('%Y-%m-%d'), 
                                             pictures)
                
                if vehicle_id:
                    st.success(translate("Véhicule ajouté avec succès!"))
                    st.rerun() # Rerun to refresh the list of vehicles
                else:
                    st.error(translate("Erreur lors de l'ajout du véhicule."))
            else:
                st.error(translate("Veuillez remplir au moins la marque, le modèle et la date de mise en circulation du véhicule."))

def show_edit_vehicle_form(user_id, vehicle_data):
    """Displays a form to edit an existing vehicle."""
    vehicle_id, marque, model, date_circulation, pic_inter1, pic_inter2, pic_exter1, pic_exter2 = vehicle_data

    st.subheader(f"{translate('Modifier le véhicule')}: {marque} {model}")
    with st.form(key=f"edit_vehicle_form_{vehicle_id}"):
        # Use columns for vehicle details
        col_edit_veh_details1, col_edit_veh_details2 = st.columns(2)
        with col_edit_veh_details1:
            new_marque = st.text_input(translate("Marque du véhicule"), value=marque, key=f"edit_veh_marque_{vehicle_id}")
            new_model = st.text_input(translate("Modèle du véhicule"), value=model, key=f"edit_veh_model_{vehicle_id}")
        with col_edit_veh_details2:
            current_date_circulation = datetime.datetime.strptime(date_circulation, '%Y-%m-%d').date() if date_circulation else date.today()
            new_date_circulation = st.date_input(translate("Date de mise en circulation"), value=current_date_circulation, key=f"edit_veh_date_circulation_{vehicle_id}")
        
        st.markdown("---")
        st.subheader(translate("Images du véhicule"))

        # Display current images and allow new uploads in columns
        current_pics = {
            'inter1': pic_inter1, 'inter2': pic_inter2,
            'exter1': pic_exter1, 'exter2': pic_exter2
        }
        uploaded_pics = {}
        
        # Group image display and uploaders into two columns
        col_current_img1, col_current_img2 = st.columns(2)
        col_upload_img1, col_upload_img2 = st.columns(2)

        with col_current_img1:
            st.write(translate("Images intérieures actuelles"))
            display_full_path_image(current_pics['inter1'], translate("Intérieur 1"), width=80)
            display_full_path_image(current_pics['inter2'], translate("Intérieur 2"), width=80)
        with col_current_img2:
            st.write(translate("Images extérieures actuelles"))
            display_full_path_image(current_pics['exter1'], translate("Extérieur 1"), width=80)
            display_full_path_image(current_pics['exter2'], translate("Extérieur 2"), width=80)

        with col_upload_img1:
            uploaded_pics['inter1'] = st.file_uploader(translate("Changer Intérieur 1"), type=["jpg", "jpeg", "png"], key=f"edit_veh_inter1_{vehicle_id}")
            uploaded_pics['inter2'] = st.file_uploader(translate("Changer Intérieur 2"), type=["jpg", "jpeg", "png"], key=f"edit_veh_inter2_{vehicle_id}")
        with col_upload_img2:
            uploaded_pics['exter1'] = st.file_uploader(translate("Changer Extérieur 1"), type=["jpg", "jpeg", "png"], key=f"edit_veh_exter1_{vehicle_id}")
            uploaded_pics['exter2'] = st.file_uploader(translate("Changer Extérieur 2"), type=["jpg", "jpeg", "png"], key=f"edit_veh_exter2_{vehicle_id}")


        col_buttons = st.columns(2)
        with col_buttons[0]:
            submitted = st.form_submit_button(translate("Enregistrer les modifications"))
        with col_buttons[1]:
            canceled = st.form_submit_button(translate("Annuler"))

        if canceled:
            st.session_state.editing_vehicle_id = None # Exit edit mode
            st.rerun()

        if submitted:
            if new_marque and new_model and new_date_circulation:
                new_pictures_to_save = {}
                for key, uploaded_file in uploaded_pics.items():
                    if uploaded_file:
                        new_pictures_to_save[key] = save_vehicle_image(uploaded_file, user_id, f"{key}_updated")
                    else:
                        new_pictures_to_save[key] = current_pics[key]
                
                with sqlite3.connect('priminsberg_rides.db') as conn:
                    c = conn.cursor()
                    c.execute('''
                        UPDATE vehicul SET marque=?, model=?, date_mise_en_circulation=?
                        WHERE id=? AND user_id=?
                    ''', (new_marque, new_model, new_date_circulation.strftime('%Y-%m-%d'), vehicle_id, user_id))
                    conn.commit()

                if update_vehicul_pictures(vehicle_id, new_pictures_to_save):
                    st.success(translate("Véhicule mis à jour avec succès!"))
                    st.session_state.editing_vehicle_id = None # Exit edit mode
                    st.rerun()
                else:
                    st.error(translate("Erreur lors de la mise à jour des images du véhicule."))
            else:
                st.error(translate("Veuillez remplir tous les champs obligatoires pour le véhicule."))


# --- Edit Profile Page (Modified to include Vehicle Management) ---

def show_edit_profile():
    """
    Displays the form to edit user profile information and manage vehicles.
    """
    user = st.session_state.current_user
    user_id = user[0]

    # --- Section 1: Edit Personal Information ---
    styled_subheader(translate("Modifier mes informations personnelles"))
    with st.form(key="edit_profile_form"):
        # Create two columns for personal info fields
        col1_personal, col2_personal = st.columns(2)

        with col1_personal:
            first_name = st.text_input(translate("Prénom"), value=user[3], key="edit_profile_first_name")
            last_name = st.text_input(translate("Nom de famille"), value=user[4], key="edit_profile_last_name")
            station = st.text_input(translate("Gare"), value=user[5], key="edit_profile_station")
        
        with col2_personal:
            phone = st.text_input(translate("Téléphone"), value=user[7], key="edit_profile_phone")
            email = st.text_input(translate("Email"), value=user[6], key="edit_profile_email")
            # Convert string date from DB to datetime.date object for st.date_input
            current_license_date = datetime.datetime.strptime(user[8], '%Y-%m-%d').date() if user[8] else date.today()
            driving_license_date = st.date_input(translate("Date d'obtention du permis"), value=current_license_date, key="edit_license_date")
        
        # Profile picture upload functionality (now also in columns)
        st.markdown("---")
        st.subheader(translate("Photo de profil"))
        col_profile_pic_display, col_profile_pic_uploader = st.columns([1, 2]) # Adjusted ratio for display vs uploader

        with col_profile_pic_display:
            current_profile_pic_path = user[9] if len(user) > 9 and user[9] else None
            display_full_path_image(current_profile_pic_path, translate("Photo de profil actuelle"), width=100)
        
        with col_profile_pic_uploader:
            st.markdown("<br>", unsafe_allow_html=True) # Add a small vertical space
            uploaded_profile_picture = st.file_uploader(translate("Changer la photo de profil"), type=["png", "jpg", "jpeg"], key="profile_picture_uploader")

        col_buttons_profile = st.columns(2)
        with col_buttons_profile[0]:
            submitted = st.form_submit_button(translate("Enregistrer les modifications du profil"))
        with col_buttons_profile[1]:
            canceled = st.form_submit_button(translate("Annuler les modifications du profil"))

        if canceled:
            st.session_state.menu_selection = "profile"
            st.rerun()

        if submitted:
            if not all([first_name, last_name, station, phone, email, driving_license_date]):
                st.error(translate("Aucun champ personnel ne peut être vide !"))
            else:
                profile_picture_path_to_save = current_profile_pic_path # Default to current path

                if uploaded_profile_picture is not None:
                    # Save the new profile picture, this function also handles deleting the old one
                    new_path = save_profile_picture(uploaded_profile_picture, user_id)
                    if new_path:
                        profile_picture_path_to_save = new_path
                        st.success(translate("Nouvelle photo de profil téléchargée avec succès !"))
                    else:
                        st.error(translate("Erreur lors du téléchargement de la nouvelle photo de profil."))

                # Update user profile in DB
                update_user_profile_db(user_id, first_name, last_name, station, email, phone, driving_license_date.strftime('%Y-%m-%d'))
                
                # Update profile picture path (if changed)
                update_user_profile_picture(user_id, profile_picture_path_to_save)

                # Refresh session state user data
                st.session_state.current_user = get_user_by_username_db(user[1]) # Fetch updated user data
                st.success(translate("Profil personnel mis à jour avec succès !"))
                st.rerun() # Rerun to reflect changes


    st.markdown("---")
    # --- Section 2: Manage Vehicles ---
    styled_subheader(translate("Gestion des Véhicules"))

    
    col_add_veh, col_list_veh = st.columns([1, 1]) 

    with col_add_veh:
        with st.expander(translate("Ajouter un nouveau véhicule"), expanded=False):
            show_add_vehicle_form(user_id)

    with col_list_veh:
        st.subheader(translate("Mes véhicules enregistrés"))
        vehicles = get_user_vehiculs_db(user_id) 

        if vehicles:
        
            if st.session_state.editing_vehicle_id:
                editing_vehicle_data = next((v for v in vehicles if v[0] == st.session_state.editing_vehicle_id), None)
                if editing_vehicle_data:
                    show_edit_vehicle_form(user_id, editing_vehicle_data)
                else:
                    st.session_state.editing_vehicle_id = None 
                    st.rerun()
            else:
             
                num_vehicles = len(vehicles)
                for i in range(0, num_vehicles, 2):
                    row_cols = st.columns(2)
                    for j in range(2):
                        if i + j < num_vehicles:
                            vehicle = vehicles[i + j]
                            vehicle_id, marque, model, date_circulation, pic_inter1, pic_inter2, pic_exter1, pic_exter2 = vehicle
                            
                            with row_cols[j]: 
                                st.markdown(f"""
                                <div class='vehicle-card'>
                                    <h4>{translate("Véhicule")}: {marque} {model}</h4>
                                    <p><strong>{translate('Marque')}:</strong> {marque}</p>
                                    <p><strong>{translate('Modèle')}:</strong> {model}</p>
                                    <p><strong>{translate('Date de mise en circulation')}:</strong> {date_circulation}</p>
                                """, unsafe_allow_html=True)

                               
                                card_image_cols = st.columns(2) 
                                with card_image_cols[0]:
                                    display_full_path_image(pic_inter1, translate("Intérieur 1"), width=80)
                                    display_full_path_image(pic_inter2, translate("Intérieur 2"), width=80)
                                with card_image_cols[1]:
                                    display_full_path_image(pic_exter1, translate("Extérieur 1"), width=80)
                                    display_full_path_image(pic_exter2, translate("Extérieur 2"), width=80)
                                
                                col_actions = st.columns(2)
                                with col_actions[0]:
                                    if st.button(translate("Modifier ce véhicule"), key=f"edit_veh_{vehicle_id}"):
                                        st.session_state.editing_vehicle_id = vehicle_id
                                        st.rerun()
                                with col_actions[1]:
                                    delete_button_key = f"delete_veh_{vehicle_id}"
                                    confirm_delete_button_key = f"confirm_delete_veh_{vehicle_id}"

                                    if st.button(translate("Supprimer ce véhicule"), key=delete_button_key):
                                        st.session_state[f'confirm_delete_{vehicle_id}'] = True
                                        st.rerun()

                                if st.session_state.get(f'confirm_delete_{vehicle_id}', False):
                                    st.warning(translate("Êtes-vous sûr de vouloir supprimer ce véhicule et toutes ses images ? Cette action est irréversible."))
                                    if st.button(translate("Confirmer la suppression"), key=confirm_delete_button_key):
                                        for img_path in [pic_inter1, pic_inter2, pic_exter1, pic_exter2]:
                                            if img_path:
                                                delete_image(img_path)
                                        with sqlite3.connect('priminsberg_rides.db') as conn:
                                            c = conn.cursor()
                                            c.execute("DELETE FROM vehicul WHERE id=?", (vehicle_id,))
                                            conn.commit()
                                        st.success(translate("Véhicule supprimé avec succès !"))
                                        st.session_state[f'confirm_delete_{vehicle_id}'] = False
                                        st.rerun()
                                    if st.button(translate("Annuler la suppression"), key=f"cancel_delete_veh_{vehicle_id}"):
                                        st.session_state[f'confirm_delete_{vehicle_id}'] = False
                                        st.rerun()

                                st.markdown("</div>", unsafe_allow_html=True) 
                                st.markdown("---")
        else:
            st.info(translate("Aucun véhicule enregistré pour le moment. Utilisez le formulaire ci-dessus pour en ajouter un."))



if __name__ == "__main__":
    main()
