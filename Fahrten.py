import streamlit as st
import sqlite3
import bcrypt
import datetime
from datetime import date
from PIL import Image
import os
import base64
from io import BytesIO
from Rides import show_display_rides,show_offer_ride,show_my_rides
from Css import style_css

def get_db_connection():
    conn = sqlite3.connect('priminsberg_rides.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- Configuration des dossiers pour les images ---
UPLOAD_DIR = "uploads"
PROFILE_PICTURES_DIR = os.path.join(UPLOAD_DIR, "profile_pictures")
VEHICLE_PICTURES_DIR = os.path.join(UPLOAD_DIR, "vehicle_pictures")

# Assurez-vous que les dossiers existent
os.makedirs(PROFILE_PICTURES_DIR, exist_ok=True)
os.makedirs(VEHICLE_PICTURES_DIR, exist_ok=True)

# --- Importations des modules locaux ---
from Database_Fahrten import (
    setup_db, add_vehicul_db, save_vehicle_image, save_profile_picture, save_image,
    update_user_profile_picture, update_vehicul_pictures, delete_image, display_image,
    register_user_db, get_user_by_username_db, update_user_profile_db,
    add_ride_db, get_rides_db, delete_ride_db, update_ride_db,
    book_ride_db, get_user_bookings_db, get_user_vehiculs_db
)
from Utils_Fahrten import display_logo, hash_password, verify_password, translate, get_base64_icon

# --- Helper Functions for UI ---

def display_app_header(page_title):
    style_css()
    
    col1, col2 = st.columns([0.8, 5])
    with col1:
        display_logo(os.path.join("Images", "Logo_MitFahrn.PNG"), width=150)
    with col2:
        st.markdown(f"""
        <h1 style='color: #f10000; font-weight: bold; border-bottom: 2px solid #8c8c8c; padding-bottom: 10px;'>
            {translate(page_title)}
        </h1>
        """, unsafe_allow_html=True)
    st.markdown("---")

def styled_subheader(text):
    """Displays a styled subheader."""
    st.markdown(f"""
    <h2 style='color: #f10000; font-weight: bold; margin-top: 20px;'>
        {translate(text)}
    </h2>
    """, unsafe_allow_html=True)

def image_to_base64(image):
    """Convert PIL Image to base64 string"""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def display_full_path_image(image_relative_path, caption, width=None, circle=False):
    """
    Displays an image from a path relative to UPLOAD_DIR.
    Includes option to display in a colored circle.
    """
    if image_relative_path:
        normalized_relative_path = image_relative_path.replace('\\', '/')
        full_path = os.path.join(UPLOAD_DIR, normalized_relative_path)

        if os.path.exists(full_path):
            try:
                image = Image.open(full_path)
                if circle:
                    # Use custom CSS for circular images
                    st.markdown(f"""
                    <div style="text-align: center; margin: 10px 0;">
                        <img src="data:image/png;base64,{image_to_base64(image)}" 
                             class="{'profile-picture-circle' if width==150 else 'vehicle-picture-circle'}" 
                             style="width: {width}px; height: {width}px; object-fit: cover;">
                        <p style="text-align: center; margin-top: 5px; font-weight: bold;">{caption}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.image(image, caption=caption, width=width)
            except Exception as e:
                st.warning(f"{translate('Impossible de charger l\'image')} {os.path.basename(full_path)}: {e}")
        else:
            st.info(f"{translate('Image non trouvée pour')} {caption} ({image_relative_path}).")
    else:
        st.info(f"{translate('Pas de chemin d\'image fourni pour')} {caption}.")

# --- Main Application Logic ---

def main():
    style_css()
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

  

    # --- Session State Initialization ---
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'page' not in st.session_state:
        st.session_state.page = "landing"
    if 'menu_selection' not in st.session_state:
        st.session_state.menu_selection = "profile"
    if 'editing_vehicle_id' not in st.session_state:
        st.session_state.editing_vehicle_id = None

    # --- Conditional Page Rendering ---
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
            <h2 style="color: white; font-size: 1.5em; font-weight: bold; 
                        border-bottom: 2px solid var(--accent-red); padding-bottom: 10px;">
                {translate("Bienvenue")}, {st.session_state.current_user[3]}!
            </h2>
        </div>
        """, unsafe_allow_html=True)

        menu_items = [
            (translate("Mon Profil"), "profile"),
            (translate("Fahrten anzeigen"), "display_rides"),
            (translate("Proposer un trajet"), "offer_ride"),
            (translate("Mes trajets"), "my_rides"),
            (translate("Modifier le profil"), "edit_profile")
        ]

        for label, key_name in menu_items:
            if st.sidebar.button(label, key=f"menu_{key_name}"):
                st.session_state.menu_selection = key_name
                st.session_state.editing_vehicle_id = None
                st.rerun()

        if st.sidebar.button(translate("Se déconnecter"), key="sidebar_logout_btn"):
            st.session_state.current_user = None
            st.session_state.page = "landing"
            st.session_state.menu_selection = "profile"
            st.session_state.editing_vehicle_id = None
            st.rerun()


    # --- Authenticated User Main Content ---
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

# --- Page Functions ---

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
       
        if st.button(translate("Se connecter"), key="landing_login_button", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
    with col2:
        if st.button(translate("S'inscrire"), key="landing_register_button", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()

def show_login():
    """Displays the login form."""
    with st.form(key="login_form"):
        username = st.text_input(translate("Nom d'utilisateur"), key="login_username")
        password = st.text_input(translate("Mot de passe"), type="password", key="login_password")

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button(translate("Se connecter"), use_container_width=True):
                user = get_user_by_username_db(username)
                if user and verify_password(password, user[2]):
                    st.session_state.current_user = user
                    st.session_state.page = "profile"
                    st.session_state.menu_selection = "profile"
                    st.rerun()
                else:
                    st.error(translate("Échec de la connexion ! Nom d'utilisateur ou mot de passe invalide."))
        with col2:
            if st.form_submit_button(translate("Retour"), use_container_width=True):
                st.session_state.page = "landing"
                st.rerun()

def show_register():
    """Displays the user registration form."""
    with st.form(key="register_form"):
        username = st.text_input(translate("Nom d'utilisateur"), key="register_username")
        password = st.text_input(translate("Mot de passe"), type="password", key="register_password")
        first_name = st.text_input(translate("Prénom"), key="register_first_name")
        last_name = st.text_input(translate("Nom de famille"), key="register_last_name")
        station = st.text_input(translate("Gare"), help=translate("Votre gare habituelle, ex : 'Hauptbahnhof'"), key="register_station")
        email = st.text_input(translate("Email"), key="register_email")
        phone = st.text_input(translate("Téléphone"), key="register_phone")
        
        profile_picture_file = st.file_uploader(translate("Photo de profil (Optionnel)"), 
                                             type=["jpg", "jpeg", "png"], 
                                             key="register_profile_pic_uploader")
        
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
                    user_id = register_user_db(username, pw_hash, first_name, last_name, station, email, phone, driving_license_date.strftime('%Y-%m-%d'), None)

                    if user_id:
                        profile_pic_path = None
                        if profile_picture_file is not None:
                            profile_pic_path = save_profile_picture(profile_picture_file, user_id)
                            if profile_pic_path:
                                update_user_profile_picture(user_id, profile_pic_path)
                                st.success(translate("Photo de profil téléchargée avec succès !"))
                        
                        st.session_state.current_user = get_user_by_username_db(username)
                        st.success(translate("Inscription terminée !"))
                        st.session_state.page = "profile"
                        st.session_state.menu_selection = "profile"
                        st.rerun()
                    else:
                        st.error(translate("Ce nom d'utilisateur existe déjà !"))
                except Exception as e:
                    st.error(f"{translate('Une erreur est survenue lors de l\'inscription')} : {e}")

def show_profile():
    """Displays the user's profile information."""
    user = st.session_state.current_user
    user_id = user[0]

    st.markdown(f"""
    <div class='info-card'>
        <h3 style='color: var(--accent-red); margin-top: 0;'>{translate("Informations de profil")}</h3>
    """, unsafe_allow_html=True)

    # Display User Profile Picture in circle
    
    profile_picture_path = user[9] if len(user) > 9 else None
    col1, col2,col3  = st.columns(3)
    with col1:
        
        display_full_path_image(profile_picture_path, translate("Profil"), width=250, circle=True)
    with col2:
        styled_subheader(translate("Mes Informations :"))
        
        st.write(f"**{translate('Nom d\'utilisateur')} :** {user[1]}")
        st.write(f"**{translate('Prénom')} :** {user[3]}")
        st.write(f"**{translate('Nom de famille')} :** {user[4]}")
        st.write(f"**{translate('Téléphone')} :** {user[7]}")
        st.write(f"**{translate('Email')} :** {user[6]}")
    
        st.write(f"**{translate('Date d\'obtention du permis')} :** {user[8]}")
    with col3:
       # styled_subheader(translate(""))
       # st.write(f"**{translate('Gare')} :** {user[5]}")
       styled_subheader(translate("Mes Trajets :"))  

   # st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    styled_subheader(translate("Mes Véhicules"))

    vehicles = get_user_vehiculs_db(user_id)

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
                display_full_path_image(pic_inter1, translate("Intérieur 1"), width=350)
            with image_cols[1]:
                display_full_path_image(pic_inter2, translate("Intérieur 2"), width=350)
            with image_cols[2]:
                display_full_path_image(pic_exter1, translate("Extérieur 1"), width=350)
            with image_cols[3]:
                display_full_path_image(pic_exter2, translate("Extérieur 2"), width=350)
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("---")
    else:
        st.info(translate("Aucun véhicule enregistré pour le moment."))

def update_password_db(user_id, hashed_new_password):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_new_password, user_id))
    conn.commit()
    conn.close()

def check_password_db(user_id, hashed_password):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE id = ?", (user_id,))
    stored_hashed_password = c.fetchone()
    conn.close()
    if stored_hashed_password and stored_hashed_password[0] == hashed_password:
        return True
    return False



def show_edit_profile():
    if "show_password_form" not in st.session_state:
        st.session_state.show_password_form = False
    if "editing_vehicle_id" not in st.session_state:
        st.session_state.editing_vehicle_id = None

    user = st.session_state.current_user
    user_id = user[0]

    # Section 1: Edit Personal Information & Profile Picture
    
    col1, col2, = st.columns([0.5, 1])

    # Col 1: Profile picture + password
    with col1:
        current_profile_pic_path = user[9] if len(user) > 9 and user[9] else None
        display_full_path_image(current_profile_pic_path, translate("Profil"), width=230, circle=True)
        if st.button(translate("Changer le mot de passe"), key="btn_show_password_form_col1", use_container_width=True):
            st.session_state.show_password_form = not st.session_state.show_password_form

        if st.session_state.show_password_form:
            styled_subheader(translate("Changer le mot de passe"))
            with st.form(key="change_password_form"):
                old_password = st.text_input(translate("Ancien mot de passe"), type="password", key="old_password")
                new_password = st.text_input(translate("Nouveau mot de passe"), type="password", key="new_password")
                confirm_new_password = st.text_input(translate("Confirmer le nouveau mot de passe"), type="password", key="confirm_new_password")

                col_password_buttons = st.columns(2)
                with col_password_buttons[0]:
                    password_submitted = st.form_submit_button(translate("Enregistrer le nouveau mot de passe"), use_container_width=True)
                with col_password_buttons[1]:
                    password_canceled = st.form_submit_button(translate("Annuler"), use_container_width=True)

                if password_canceled:
                    st.session_state.show_password_form = False
                    st.rerun()

                if password_submitted:
                    if not old_password or not new_password or not confirm_new_password:
                        st.error(translate("Le mot de passe ne peut pas être vide."))
                    elif new_password != confirm_new_password:
                        st.error(translate("Les nouveaux mots de passe ne correspondent pas."))
                    else:
                        hashed_old_password = hash_password(old_password)
                        if check_password_db(user_id, hashed_old_password):
                            hashed_new_password = hash_password(new_password)
                            update_password_db(user_id, hashed_new_password)
                            st.success(translate("Mot de passe mis à jour avec succès !"))
                            st.session_state.show_password_form = False
                            st.rerun()
                        else:
                            st.error(translate("Mot de passe actuel incorrect."))

    # Col 2 & Col 3: Personal info form
    with st.form(key="edit_profile_form"):
        
        
        
        with col2:
            styled_subheader(translate("Modifier mes informations :"))
            col1, col2 = st.columns([1, 1])

    # Col 1: Profile picture + password
            with col1:

                first_name = st.text_input(translate("Prénom"), value=user[3], key="edit_profile_first_name")
                last_name = st.text_input(translate("Nom de famille"), value=user[4], key="edit_profile_last_name")
                current_license_date = datetime.datetime.strptime(user[8], '%Y-%m-%d').date() if user[8] else date.today()
                st.date_input(translate("Date d'obtention du permis"), value=current_license_date, key="display_license_date", disabled=True)

            with col2:
                
                phone = st.text_input(translate("Téléphone"), value=user[7], key="edit_profile_phone")
                email = st.text_input(translate("Email"), value=user[6], key="edit_profile_email")

        col_buttons_profile = st.columns(2)
        with col_buttons_profile[0]:
            submitted = st.form_submit_button(translate("Enregistrer les modifications du profil"), use_container_width=True)
        with col_buttons_profile[1]:
            canceled = st.form_submit_button(translate("Annuler les modifications du profil"), use_container_width=True)

        if canceled:
            st.session_state.menu_selection = "profile"
            st.rerun()

        if submitted:
            if not all([first_name, last_name, phone, email]):
                st.error(translate("Aucun champ personnel ne peut être vide !"))
            else:
                update_user_profile_db(user_id, first_name, last_name, email, phone, user[8])
                update_user_profile_picture(user_id, current_profile_pic_path)
                st.session_state.current_user = get_user_by_username_db(user[1])
                st.success(translate("Profil personnel mis à jour avec succès !"))
                st.rerun()

    # Section 2: Vehicle Management
    styled_subheader(translate("Gestion des Véhicules"))
    col_list_veh, col_add_veh = st.columns([1, 1], gap="small")

    with col_list_veh:
        st.subheader(translate("Mes véhicules enregistrés"))
        vehicles = get_user_vehiculs_db(user_id)

        if vehicles:
            if st.session_state.editing_vehicle_id:
                editing_vehicle_data = next((v for v in vehicles if v[0] == st.session_state.editing_vehicle_id), None)
                
            else:
                for vehicle in vehicles:
                    vehicle_id, marque, model, date_circulation, pic_inter1, pic_inter2, pic_exter1, pic_exter2 = vehicle
                    st.markdown(f"""
                        <div class='vehicle-card'>
                            <h4>{translate("Véhicule")}: {marque} {model}</h4>
                            <p><strong>{translate('Marque')}:</strong> {marque}</p>
                            <p><strong>{translate('Modèle')}:</strong> {model}</p>
                            <p><strong>{translate('Date de mise en circulation')}:</strong> {date_circulation}</p>
                    """, unsafe_allow_html=True)
                    img_cols = st.columns(2)
                    with img_cols[0]:
                        display_full_path_image(pic_inter1, translate("Intérieur 1"), width=200)
                        display_full_path_image(pic_inter2, translate("Intérieur 2"), width=200)
                    with img_cols[1]:
                        display_full_path_image(pic_exter1, translate("Extérieur 1"), width=200)
                        display_full_path_image(pic_exter2, translate("Extérieur 2"), width=200)

                    action_cols = st.columns(2)
                    with action_cols[0]:
                        if st.button(translate("Modifier ce véhicule"), key=f"edit_veh_{vehicle_id}", use_container_width=True):
                            st.session_state.editing_vehicle_id = vehicle_id
                            st.rerun()
                    with action_cols[1]:
                        if st.button(translate("Supprimer ce véhicule"), key=f"delete_veh_{vehicle_id}", use_container_width=True):
                            for img_path in [pic_inter1, pic_inter2, pic_exter1, pic_exter2]:
                                if img_path:
                                    delete_image(img_path)
                            with sqlite3.connect('priminsberg_rides.db') as conn:
                                c = conn.cursor()
                                c.execute("DELETE FROM vehicul WHERE id=?", (vehicle_id,))
                                conn.commit()
                            st.success(translate("Véhicule supprimé avec succès !"))
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.markdown("---")
        else:
            st.info(translate("Vous n'avez pas encore de véhicules enregistrés."))

    with col_add_veh:
        with st.expander(translate("Ajouter un nouveau véhicule"), expanded=False):
            with st.form(key="add_vehicle_form"):
                col1, col2 = st.columns(2)
                with col1:
                    marque = st.text_input(translate("Marque du véhicule"), key="add_veh_marque")
                    model = st.text_input(translate("Modèle du véhicule"), key="add_veh_model")
                with col2:
                    date_mise_en_circulation = st.date_input(translate("Date de mise en circulation"), key="add_veh_date_circulation")

                st.subheader(translate("Images du véhicule (Optionnel)"))
                img1, img2 = st.columns(2)
                with img1:
                    inter1 = st.file_uploader(translate("Image intérieure 1"), type=["jpg", "jpeg", "png"], key="add_veh_inter1")
                    inter2 = st.file_uploader(translate("Image intérieure 2"), type=["jpg", "jpeg", "png"], key="add_veh_inter2")
                with img2:
                    exter1 = st.file_uploader(translate("Image extérieure 1"), type=["jpg", "jpeg", "png"], key="add_veh_exter1")
                    exter2 = st.file_uploader(translate("Image extérieure 2"), type=["jpg", "jpeg", "png"], key="add_veh_exter2")

                if st.form_submit_button(translate("Ajouter le véhicule"), use_container_width=True):
                    if marque and model and date_mise_en_circulation:
                        pictures = {
                            'inter1': save_vehicle_image(inter1, user_id, "inter1") if inter1 else None,
                            'inter2': save_vehicle_image(inter2, user_id, "inter2") if inter2 else None,
                            'exter1': save_vehicle_image(exter1, user_id, "exter1") if exter1 else None,
                            'exter2': save_vehicle_image(exter2, user_id, "exter2") if exter2 else None
                        }
                        vehicle_id = add_vehicul_db(user_id, marque, model, date_mise_en_circulation.strftime('%Y-%m-%d'), pictures)
                        if vehicle_id:
                            st.success(translate("Véhicule ajouté avec succès!"))
                            st.rerun()
                    else:
                        st.error(translate("Marque, modèle et date de mise en circulation sont obligatoires."))



# --- Entry Point ---
if __name__ == "__main__":
    main()