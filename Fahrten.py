import streamlit as st
import sqlite3
import bcrypt
import datetime
from datetime import date
from PIL import Image
import os
import base64

def get_base64_icon(image_path):
    try:
        full_path = os.path.join(os.path.dirname(__file__), image_path)
        with open(full_path, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        return encoded_string
    except FileNotFoundError:
        st.error(f"Erreur : Fichier d'icône introuvable à '{image_path}'. Vérifiez le chemin.")
        return None
    except Exception as e:
        st.error(f"Erreur lors du chargement de l'icône : {e}")
        return None

def display_logo(image_path, width=200):
    try:
        full_path = os.path.join(os.path.dirname(__file__), image_path)
        img = Image.open(full_path)
        st.image(img, width=width)
    except FileNotFoundError:
        st.error(f"Erreur : Image introuvable à '{image_path}'. Vérifiez le chemin.")
    except Exception as e:
        st.error(f"Erreur lors du chargement de l'image : {e}")

def setup_db():
    with sqlite3.connect('priminsberg_rides.db') as conn:
        c = conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            station TEXT,
            email TEXT,
            phone TEXT
        )''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS rides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider_id INTEGER,
            start_location TEXT,
            destination TEXT,
            date TEXT,
            time TEXT,
            available_seats INTEGER,
            FOREIGN KEY(provider_id) REFERENCES users(id)
        )
        ''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ride_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(ride_id) REFERENCES rides(id)
        )
        ''')
        conn.commit()

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode(), hashed_password)

def display_app_header(page_title):
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        display_logo(os.path.join("Images", "Logo_MitFahrn.PNG"), width=100)
    with col2:
        st.markdown(f"""
        <h1 style='color: var(--accent-red); font-weight: bold; border-bottom: 2px solid var(--secondary-gray); padding-bottom: 10px;'>
            {page_title}
        </h1>
        """, unsafe_allow_html=True)
    st.markdown("---")

def styled_subheader(text):
    st.markdown(f"""
    <h2 style='color: var(--accent-red); font-weight: bold; margin-top: 20px;'>
        {text}
    </h2>
    """, unsafe_allow_html=True)

def main():
    icon_base64 = get_base64_icon(os.path.join("Images", "Logo_MitFahrn.ico"))
    if icon_base64:
        st.set_page_config(
            layout="wide",
            page_title="Gestion des trajets Priminsberg",
            page_icon=f"data:image/x-icon;base64,{icon_base64}",
            initial_sidebar_state="expanded"
        )
    else:
        st.set_page_config(
            layout="wide",
            page_title="Gestion des trajets Priminsberg",
            initial_sidebar_state="expanded"
        )

    setup_db()

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
        .stNumberInput > div > input {
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
        .stSelectbox > label {
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

    </style>
    """, unsafe_allow_html=True)

    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'page' not in st.session_state:
        st.session_state.page = "landing"
    if 'menu_selection' not in st.session_state:
        st.session_state.menu_selection = "profile"

    if st.session_state.current_user is None:
        if st.session_state.page == "login":
            display_app_header("Connexion")
            show_login()
        elif st.session_state.page == "register":
            display_app_header("Inscription")
            show_register()
        else:
            display_app_header("Bienvenue sur Priminsberg Ride")
            show_landing()
    else:
        st.sidebar.markdown(f"""
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: var(--accent-red); font-size: 1.5em; font-weight: bold; 
                        border-bottom: 2px solid var(--dark-red-accent); padding-bottom: 10px;">
                Bienvenue, {st.session_state.current_user[3]}!
            </h2>
        </div>
        """, unsafe_allow_html=True)

        menu_items = [
            ("Mon Profil", "profile"),
            ("Afficher les trajets", "display_rides"),
            ("Proposer un trajet", "offer_ride"),
            ("Mes trajets", "my_rides"),
            ("Modifier le profil", "edit_profile")
        ]

        for label, key_name in menu_items:
            if st.sidebar.button(label, key=f"menu_{key_name}"):
                st.session_state.menu_selection = key_name
                st.rerun()

        if st.sidebar.button("Se déconnecter", key="sidebar_logout_btn"):
            st.session_state.current_user = None
            st.session_state.page = "landing"
            st.session_state.menu_selection = "profile"
            st.rerun()

    if st.session_state.current_user is not None:
        if st.session_state.menu_selection == "profile":
            display_app_header("Mon Profil")
            show_profile()
        elif st.session_state.menu_selection == "display_rides":
            display_app_header("Trajets disponibles")
            show_display_rides()
        elif st.session_state.menu_selection == "offer_ride":
            display_app_header("Proposer un trajet")
            show_offer_ride()
        elif st.session_state.menu_selection == "my_rides":
            display_app_header("Mes trajets")
            show_my_rides()
        elif st.session_state.menu_selection == "edit_profile":
            display_app_header("Modifier le profil")
            show_edit_profile()

def show_landing():
    st.markdown("""
    <div style='background-color: var(--light-gray); padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h3 style='color: var(--accent-red);'>Bienvenue sur la plateforme de covoiturage Priminsberg</h3>
        <p>Connectez-vous ou inscrivez-vous pour accéder à toutes les fonctionnalités.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Se connecter", key="landing_login_button"):
            st.session_state.page = "login"
            st.rerun()
    with col2:
        if st.button("S'inscrire", key="landing_register_button"):
            st.session_state.page = "register"
            st.rerun()

def show_login():
    with st.form(key="login_form"):
        username = st.text_input("Nom d'utilisateur", key="login_username")
        password = st.text_input("Mot de passe", type="password", key="login_password")

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Se connecter"):
                with sqlite3.connect('priminsberg_rides.db') as conn:
                    c = conn.cursor()
                    c.execute("SELECT id, username, password, first_name, last_name, station, email, phone FROM users WHERE username = ?", (username,))
                    user = c.fetchone()

                if user and verify_password(password, user[2]):
                    st.session_state.current_user = user
                    st.session_state.page = "profile"
                    st.session_state.menu_selection = "profile"
                    st.rerun()
                else:
                    st.error("Échec de la connexion ! Nom d'utilisateur ou mot de passe invalide.")
        with col2:
            if st.form_submit_button("Retour"):
                st.session_state.page = "landing"
                st.rerun()

def show_register():
    with st.form(key="register_form"):
        username = st.text_input("Nom d'utilisateur", key="register_username")
        password = st.text_input("Mot de passe", type="password", key="register_password")
        first_name = st.text_input("Prénom", key="register_first_name")
        last_name = st.text_input("Nom de famille", key="register_last_name")
        station = st.text_input("Gare", help="Votre gare habituelle, ex : 'Hauptbahnhof'", key="register_station")
        email = st.text_input("Email", key="register_email")
        phone = st.text_input("Téléphone", key="register_phone")

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("S'inscrire")
            if submitted:
                if not all([username, password, first_name, last_name, station, email, phone]):
                    st.error("Veuillez remplir tous les champs !")
                else:
                    try:
                        pw_hash = hash_password(password)
                        with sqlite3.connect('priminsberg_rides.db') as conn:
                            c = conn.cursor()
                            c.execute("INSERT INTO users (username, password, first_name, last_name, station, email, phone) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                      (username, pw_hash, first_name, last_name, station, email, phone))
                            user_id = c.lastrowid
                            c.execute("SELECT id, username, password, first_name, last_name, station, email, phone FROM users WHERE id=?", (user_id,))
                            user = c.fetchone()

                        st.session_state.current_user = user
                        st.success("Inscription terminée !")
                        st.session_state.page = "profile"
                        st.session_state.menu_selection = "profile"
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Ce nom d'utilisateur existe déjà !")
        with col2:
            if st.form_submit_button("Retour"):
                st.session_state.page = "landing"
                st.rerun()

def show_profile():
    user = st.session_state.current_user

    st.markdown("""
    <div class='info-card'>
        <h3 style='color: var(--accent-red); margin-top: 0;'>Informations de profil</h3>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Nom d'utilisateur :** {user[1]}")
        st.write(f"**Prénom :** {user[3]}")
        st.write(f"**Nom de famille :** {user[4]}")
    with col2:
        st.write(f"**Gare :** {user[5]}")
        st.write(f"**Téléphone :** {user[7]}")
        st.write(f"**Email :** {user[6]}")

    st.markdown("</div>", unsafe_allow_html=True)

def show_display_rides():
    with sqlite3.connect('priminsberg_rides.db') as conn:
        c = conn.cursor()
        c.execute("DELETE FROM rides WHERE available_seats <= 0 OR SUBSTR(date,7,4)||SUBSTR(date,4,2)||SUBSTR(date,1,2) < STRFTIME('%Y%m%d','now')")
        conn.commit()

        c.execute('''
            SELECT r.id, u.username, r.start_location, r.destination, r.date, r.time, r.available_seats,
                   u.first_name, u.last_name, u.email, u.phone
            FROM rides r
            JOIN users u ON r.provider_id = u.id
            WHERE r.available_seats > 0
              AND SUBSTR(r.date,7,4)||SUBSTR(r.date,4,2)||SUBSTR(r.date,1,2) >= STRFTIME('%Y%m%d','now')
              AND r.provider_id != ?
              AND r.id NOT IN (SELECT ride_id FROM bookings WHERE user_id=?)
            ORDER BY SUBSTR(r.date,7,4)||SUBSTR(r.date,4,2)||SUBSTR(r.date,1,2) ASC, r.time ASC
        ''', (st.session_state.current_user[0], st.session_state.current_user[0]))
        rows = c.fetchall()

    if not rows:
        st.info("Aucun trajet réservable trouvé.")
    else:
        for r in rows:
            with st.expander(f"{r[2]} → {r[3]}, {r[4]} {r[5]}, Fournisseur : {r[1]}, Sièges : {r[6]}", expanded=False):
                st.markdown(f"""
                <div style='background-color: var(--light-gray); padding: 15px; border-radius: 10px;'>
                    <h4 style='color: var(--accent-red); margin-top: 0;'>Détails du trajet</h4>
                    <p><strong>Itinéraire :</strong> {r[2]} → {r[3]}</p>
                    <p><strong>Date :</strong> {r[4]}</p>
                    <p><strong>Heure :</strong> {r[5]}</p>
                    <p><strong>Sièges disponibles :</strong> {r[6]}</p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("""
                <div style='background-color: var(--light-gray); padding: 15px; border-radius: 10px; margin-top: 10px;'>
                    <h4 style='color: var(--accent-red); margin-top: 0;'>Informations sur le conducteur</h4>
                """, unsafe_allow_html=True)
                st.write(f"**Conducteur :** {r[7]} {r[8]}")
                st.write(f"**Nom d'utilisateur :** {r[1]}")
                st.write(f"**Email :** {r[9]}")
                st.write(f"**Téléphone :** {r[10]}")
                st.markdown("</div>", unsafe_allow_html=True)

                with sqlite3.connect('priminsberg_rides.db') as conn:
                    c = conn.cursor()
                    c.execute('''SELECT u.first_name, u.last_name, u.username, u.email, u.phone
                                FROM bookings b
                                JOIN users u ON b.user_id = u.id
                                WHERE b.ride_id=?
                             ''', (r[0],))
                    passengers = c.fetchall()

                st.markdown("""
                <div style='background-color: var(--light-gray); padding: 15px; border-radius: 10px; margin-top: 10px;'>
                    <h4 style='color: var(--accent-red); margin-top: 0;'>Passagers</h4>
                """, unsafe_allow_html=True)
                if not passengers:
                    st.write("Pas encore de passagers pour ce trajet.")
                else:
                    for p in passengers:
                        st.write(f"- {p[0]} {p[1]} (Nom d'utilisateur : {p[2]}) Téléphone : {p[4]}")
                st.markdown("</div>", unsafe_allow_html=True)

                if r[6] > 0:
                    if st.button("Réserver le trajet", key=f"book_ride_{r[0]}"):
                        with sqlite3.connect('priminsberg_rides.db') as conn:
                            c = conn.cursor()
                            c.execute("SELECT available_seats FROM rides WHERE id=?", (r[0],))
                            current_seats = c.fetchone()
                            if not current_seats or current_seats[0] <= 0:
                                st.error("Ce trajet n'est plus réservable ou n'a plus de sièges disponibles !")
                                st.rerun()
                            else:
                                c.execute("INSERT INTO bookings (user_id, ride_id) VALUES (?, ?)",
                                          (st.session_state.current_user[0], r[0]))
                                c.execute("UPDATE rides SET available_seats=available_seats-1 WHERE id=?", (r[0],))
                                conn.commit()
                                st.success("Trajet réservé avec succès !")
                                st.rerun()

    if st.button("Retour au profil", key="display_rides_back_button"):
        st.session_state.menu_selection = "profile"
        st.rerun()

def show_offer_ride():
    with st.form(key="offer_ride_form"):
        start_location = st.text_input("Lieu de départ", key="offer_start_location")
        destination = st.text_input("Destination", key="offer_destination")
        date_input = st.date_input("Date", min_value=date.today(), key="offer_date")
        time_input = st.time_input("Heure", key="offer_time")
        available_seats = st.number_input("Sièges disponibles", min_value=1, step=1, value=1, key="offer_available_seats")

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Enregistrer le trajet")
            if submitted:
                if not all([start_location, destination, date_input, time_input, available_seats]):
                    st.error("Veuillez remplir tous les champs !")
                else:
                    date_str = date_input.strftime("%d.%m.%Y")
                    time_str = time_input.strftime("%H:%M")

                    with sqlite3.connect('priminsberg_rides.db') as conn:
                        c = conn.cursor()
                        c.execute("INSERT INTO rides (provider_id, start_location, destination, date, time, available_seats) VALUES (?, ?, ?, ?, ?, ?)",
                                  (st.session_state.current_user[0], start_location, destination, date_str, time_str, available_seats))
                        conn.commit()
                    st.success("Trajet créé avec succès !")
                    st.rerun()
        with col2:
            if st.form_submit_button("Retour au profil"):
                st.session_state.menu_selection = "profile"
                st.rerun()

def show_my_rides():
    styled_subheader("Trajets réservés")
    with sqlite3.connect('priminsberg_rides.db') as conn:
        c = conn.cursor()
        c.execute(
            """SELECT r.id, u.username, r.start_location, r.destination, r.date, r.time, r.available_seats,
                      r.provider_id, b.id, u.first_name, u.last_name, u.phone, u.email
               FROM bookings b
               JOIN rides r ON b.ride_id = r.id
               JOIN users u ON r.provider_id = u.id
               WHERE b.user_id=? AND SUBSTR(r.date,7,4)||SUBSTR(r.date,4,2)||SUBSTR(r.date,1,2) >= STRFTIME('%Y%m%d','now')
               ORDER BY SUBSTR(r.date,7,4)||SUBSTR(r.date,4,2)||SUBSTR(r.date,1,2), r.time""",
            (st.session_state.current_user[0],))
        booked_rides = c.fetchall()

    if not booked_rides:
        st.info("Vous n'avez réservé aucun trajet.")
    else:
        for f in booked_rides:
            with st.expander(f"{f[2]} → {f[3]}, {f[4]} {f[5]}, Conducteur : {f[9]} {f[10]} (Nom d'utilisateur : {f[1]}) Téléphone : {f[11]}", expanded=False):
                st.markdown(f"""
                <div style='background-color: var(--light-gray); padding: 15px; border-radius: 10px;'>
                    <h4 style='color: var(--accent-red); margin-top: 0;'>Détails du trajet</h4>
                    <p><strong>Itinéraire :</strong> {f[2]} → {f[3]}</p>
                    <p><strong>Date :</strong> {f[4]}</p>
                    <p><strong>Heure :</strong> {f[5]}</p>
                    <p><strong>Conducteur :</strong> {f[9]} {f[10]} (Nom d'utilisateur : {f[1]})</p>
                    <p><strong>Email :</strong> {f[12]}</p>
                    <p><strong>Téléphone :</strong> {f[11]}</p>
                </div>
                """, unsafe_allow_html=True)

                if st.button("Annuler la réservation", key=f"cancel_booking_{f[8]}"):
                    with sqlite3.connect('priminsberg_rides.db') as conn:
                        c = conn.cursor()
                        c.execute("SELECT ride_id FROM bookings WHERE id=?", (f[8],))
                        ride_id_to_update = c.fetchone()
                        if ride_id_to_update:
                            c.execute("UPDATE rides SET available_seats=available_seats+1 WHERE id=?", (ride_id_to_update[0],))
                        c.execute("DELETE FROM bookings WHERE id=?", (f[8],))
                        conn.commit()
                    st.success("Réservation annulée !")
                    st.rerun()

    st.markdown("---")
    styled_subheader("Trajets proposés")
    with sqlite3.connect('priminsberg_rides.db') as conn:
        c = conn.cursor()
        c.execute(
            "SELECT id, start_location, destination, date, time, available_seats FROM rides WHERE provider_id=? ORDER BY SUBSTR(date,7,4)||SUBSTR(date,4,2)||SUBSTR(date,1,2), time",
            (st.session_state.current_user[0],))
        offered_rides = c.fetchall()

    if not offered_rides:
        st.info("Vous n'avez proposé aucun de vos propres trajets.")
    else:
        for f in offered_rides:
            with st.expander(f"{f[1]} → {f[2]}, {f[3]} {f[4]}, Sièges : {f[5]}", expanded=False):
                st.markdown("""
                <div style='background-color: var(--light-gray); padding: 15px; border-radius: 10px;'>
                    <h4 style='color: var(--accent-red); margin-top: 0;'>Passagers sur ce trajet</h4>
                """, unsafe_allow_html=True)
                with sqlite3.connect('priminsberg_rides.db') as conn:
                    c = conn.cursor()
                    c.execute('''SELECT u.first_name, u.last_name, u.username, u.email, u.phone
                                FROM bookings b
                                JOIN users u ON b.user_id = u.id
                                WHERE b.ride_id=?
                             ''', (f[0],))
                    passengers_on_ride = c.fetchall()
                if not passengers_on_ride:
                    st.write("Pas encore de passagers pour ce trajet.")
                else:
                    for p in passengers_on_ride:
                        st.write(f"- {p[0]} {p[1]} (Nom d'utilisateur : {p[2]}) Téléphone : {p[4]}")
                st.markdown("</div>", unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Modifier", key=f"edit_ride_{f[0]}"):
                        st.session_state.edit_ride = f[0]
                        st.rerun()
                with col2:
                    if st.button("Supprimer", key=f"delete_ride_{f[0]}"):
                        with sqlite3.connect('priminsberg_rides.db') as conn:
                            c = conn.cursor()
                            c.execute("DELETE FROM rides WHERE id=?", (f[0],))
                            c.execute("DELETE FROM bookings WHERE ride_id=?", (f[0],))
                            conn.commit()
                        st.success("Trajet supprimé !")
                        st.rerun()

    if 'edit_ride' in st.session_state and st.session_state.edit_ride is not None:
        edit_ride(st.session_state.edit_ride)
    elif st.button("Retour au profil", key="my_rides_back_button"):
        st.session_state.menu_selection = "profile"
        st.rerun()

def edit_ride(ride_id):
    with sqlite3.connect('priminsberg_rides.db') as conn:
        c = conn.cursor()
        c.execute("SELECT start_location, destination, date, time, available_seats FROM rides WHERE id=?", (ride_id,))
        r = c.fetchone()

    if not r:
        st.error("Le trajet n'existe plus !")
        if 'edit_ride' in st.session_state:
            del st.session_state.edit_ride
        st.rerun()
        return

    try:
        current_date = datetime.datetime.strptime(r[2], "%d.%m.%Y").date()
    except ValueError:
        current_date = date.today()
    try:
        current_time = datetime.datetime.strptime(r[3], "%H:%M").time()
    except ValueError:
        current_time = datetime.time(0, 0)

    with st.form(key=f"edit_ride_form_{ride_id}"):
        start_location = st.text_input("Lieu de départ", value=r[0], key=f"edit_start_location_{ride_id}")
        destination = st.text_input("Destination", value=r[1], key=f"edit_destination_{ride_id}")
        date_input = st.date_input("Date", value=current_date, min_value=date.today(), key=f"edit_date_{ride_id}")
        time_input = st.time_input("Heure", value=current_time, key=f"edit_time_{ride_id}")
        available_seats = st.number_input("Sièges disponibles", min_value=1, value=r[4], step=1, key=f"edit_available_seats_{ride_id}")

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Enregistrer")
        with col2:
            canceled = st.form_submit_button("Annuler")

        if canceled:
            if 'edit_ride' in st.session_state:
                del st.session_state.edit_ride
            st.rerun()

        if submitted:
            if not all([start_location, destination, date_input, time_input, available_seats]):
                st.error("Veuillez remplir tous les champs !")
            else:
                date_str_save = date_input.strftime("%d.%m.%Y")
                time_str_save = time_input.strftime("%H:%M")

                with sqlite3.connect('priminsberg_rides.db') as conn:
                    c = conn.cursor()
                    c.execute("UPDATE rides SET start_location=?, destination=?, date=?, time=?, available_seats=? WHERE id=?",
                              (start_location, destination, date_str_save, time_str_save, available_seats, ride_id))
                    conn.commit()
                st.success("Trajet mis à jour avec succès !")
                if 'edit_ride' in st.session_state:
                    del st.session_state.edit_ride
                st.rerun()

def show_edit_profile():
    user = st.session_state.current_user

    with st.form(key="edit_profile_form"):
        first_name = st.text_input("Prénom", value=user[3], key="edit_profile_first_name")
        last_name = st.text_input("Nom de famille", value=user[4], key="edit_profile_last_name")
        station = st.text_input("Gare", value=user[5], key="edit_profile_station")
        phone = st.text_input("Téléphone", value=user[7], key="edit_profile_phone")
        email = st.text_input("Email", value=user[6], key="edit_profile_email")

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Enregistrer")
        with col2:
            canceled = st.form_submit_button("Annuler")

        if canceled:
            st.session_state.menu_selection = "profile"
            st.rerun()


        if submitted:
            if not all([first_name, last_name, station, phone, email]):
                st.error("Aucun champ ne peut être vide !")
            else:
                with sqlite3.connect('priminsberg_rides.db') as conn:
                    c = conn.cursor()
                    c.execute("UPDATE users SET first_name=?, last_name=?, station=?, phone=?, email=? WHERE id=?",
                              (first_name, last_name, station, phone, email, user[0]))
                    conn.commit()
                    c.execute("SELECT id, username, password, first_name, last_name, station, email, phone FROM users WHERE id=?", (user[0],))
                    u = c.fetchone()
                st.session_state.current_user = u
                st.success("Profil mis à jour !")
                st.session_state.menu_selection = "profile"
                st.rerun()

if __name__ == "__main__":
    main()