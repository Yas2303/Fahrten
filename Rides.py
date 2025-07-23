import streamlit as st
import sqlite3
import bcrypt
import datetime
from datetime import date, timedelta
from PIL import Image
import os
import base64
from Database_Fahrten import setup_db
from Utils_Fahrten import display_logo, hash_password, verify_password, translate, get_base64_icon, styled_subheader
from Css import style_css
from streamlit_folium import folium_static
import folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from opencage.geocoder import OpenCageGeocode
import requests

def get_route_info(start_coords, end_coords):
    """Obtient les informations d'itinéraire (distance, durée) depuis l'API OSRM"""
    try:
        osrm_url = f"http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full"
        response = requests.get(osrm_url)
        route_data = response.json()
        
        if route_data.get('code') == 'Ok':
            distance_km = route_data['routes'][0]['distance'] / 1000  # Convertir en km
            duration_min = route_data['routes'][0]['duration'] / 60   # Convertir en minutes
            
            # Formater les résultats
            distance_str = f"{distance_km:.1f} km"
            duration_str = f"{int(duration_min // 60)}h{int(duration_min % 60):02d}" if duration_min >= 60 else f"{int(duration_min)} min"
            
            return distance_str, duration_str
        return None, None
    except:
        return None, None

def geocode_address(address):
    """Fonction pour géocoder une adresse en coordonnées GPS."""
    try:
        api_key = st.secrets["OPEN_CAGE_API_KEY"]
        geolocator = OpenCageGeocode(api_key)
        results = geolocator.geocode(address)
        if results and len(results):
            return (results[0]['geometry']['lat'], results[0]['geometry']['lng'])
        return None
    except KeyError:
        st.warning("OpenCage API key not found in secrets. Falling back to Nominatim (may be rate-limited).")
        geolocator = Nominatim(user_agent="priminsberg_rides")
        try:
            location = geolocator.geocode(address, timeout=10)
            if location:
                return (location.latitude, location.longitude)
            return None
        except GeocoderTimedOut:
            st.warning(f"Geocoding timed out for: {address}. Retrying...")
            return geocode_address(address)
        except Exception as e:
            st.error(f"Erreur de géocodage pour {address}: {e}")
            return None

def calculate_arrival_time(departure_time_str, duration_str):
    """Calcule l'heure d'arrivée estimée"""
    try:
        # Convertir l'heure de départ en objet datetime
        departure_time = datetime.datetime.strptime(departure_time_str, "%H:%M")
        
        # Extraire heures et minutes de la durée
        if 'h' in duration_str:
            hours, minutes = map(int, duration_str.replace(' min', '').split('h'))
        else:
            hours = 0
            minutes = int(duration_str.replace(' min', ''))
        
        # Calculer l'heure d'arrivée
        arrival_time = departure_time + timedelta(hours=hours, minutes=minutes)
        return arrival_time.strftime("%H:%M")
    except:
        return "N/A"


def show_my_rides():
    styled_subheader("Trajets réservés/Reservierte Fahrten")
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
            with st.expander(f"{f[2]} → {f[3]}, {f[4]} {f[5]}, Conducteur : {f[9]} {f[10]}", expanded=False):
                # Section Détails du trajet
                st.markdown(f"""
                <div style='background-color: var(--light-gray); padding: 15px; border-radius: 10px; margin-bottom: 15px;'>
                    <h4 style='color: var(--accent-red); margin-top: 0; border-bottom: 1px solid var(--accent-red); padding-bottom: 8px;'>
                        Détails du trajet
                    </h4>
                    <p style='color: white; margin-bottom: 8px;'><strong style='color: white;'>Itinéraire :</strong> {f[2]} → {f[3]}</p>
                    <p style='color: white; margin-bottom: 8px;'><strong style='color: white;'>Date :</strong> {f[4]}</p>
                    <p style='color: white;'><strong style='color: white;'>Heure de départ :</strong> {f[5]}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Section Informations sur l'itinéraire
                start_coords = geocode_address(f[2])
                end_coords = geocode_address(f[3])
                
                if start_coords and end_coords:
                    distance, duration = get_route_info(start_coords, end_coords)
                    arrival_time = calculate_arrival_time(f[5], duration) if duration else "N/A"
                    
                    st.markdown(f"""
                    <div style='background-color: var(--light-gray); padding: 15px; border-radius: 10px; margin-bottom: 15px;'>
                        <h4 style='color: var(--accent-red); margin-top: 0; border-bottom: 1px solid var(--accent-red); padding-bottom: 8px;'>
                            Informations sur l'itinéraire
                        </h4>
                        <p style='color: black; margin-bottom: 8px;'><strong style='color: black;'>Distance :</strong> {distance if distance else 'Non disponible'}</p>
                        <p style='color: black; margin-bottom: 8px;'><strong style='color: black;'>Durée estimée :</strong> {duration if duration else 'Non disponible'}</p>
                        <p style='color: black;'><strong style='color: black;'>Heure d'arrivée estimée :</strong> {arrival_time}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Section Informations conducteur
                st.markdown(f"""
                <div style='background-color: var(--light-gray); padding: 15px; border-radius: 10px; margin-bottom: 15px;'>
                    <h4 style='color: var(--accent-red); margin-top: 0; border-bottom: 1px solid var(--accent-red); padding-bottom: 8px;'>
                        Informations conducteur
                    </h4>
                    <p style='color: black; margin-bottom: 8px;'><strong style='color: black;'>Nom :</strong> {f[9]} {f[10]}</p>
                    <p style='color: black; margin-bottom: 8px;'><strong style='color: black;'>Nom d'utilisateur :</strong> {f[1]}</p>
                    <p style='color: black; margin-bottom: 8px;'><strong style='color: black;'>Email :</strong> {f[12]}</p>
                    <p style='color: black;'><strong style='color: black;'>Téléphone :</strong> {f[11]}</p>
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
    styled_subheader("Trajets proposés/Angebotene Fahrten")
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
                col_info, col_map = st.columns([1, 1])
                
                with col_info:
                    # Section Passagers
                    st.markdown("""
                    <div style='background-color: var(--light-gray); padding: 15px; border-radius: 10px; margin-bottom: 15px;'>
                        <h4 style='color: var(--accent-red); margin-top: 0; border-bottom: 1px solid var(--accent-red); padding-bottom: 8px;'>
                            Passagers sur ce trajet
                        </h4>
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
                        st.markdown("<p style='color: white;'>Pas encore de passagers pour ce trajet.</p>", unsafe_allow_html=True)
                    else:
                        for p in passengers_on_ride:
                            st.markdown(f"<p style='color: white; margin-bottom: 8px;'>- {p[0]} {p[1]} (<strong style='color: white;'>Nom d'utilisateur</strong> : {p[2]}) <strong style='color: white;'>Téléphone</strong> : {p[4]}</p>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Section Informations itinéraire
                    st.markdown("""
                    <div style='background-color: var(--light-gray); padding: 15px; border-radius: 10px; margin-bottom: 15px;'>
                        <h4 style='color: var(--accent-red); margin-top: 0; border-bottom: 1px solid var(--accent-red); padding-bottom: 8px;'>
                            Informations sur l'itinéraire
                        </h4>
                    """, unsafe_allow_html=True)
                    
                    start_coords = geocode_address(f[1])
                    end_coords = geocode_address(f[2])
                    
                    if start_coords and end_coords:
                        distance, duration = get_route_info(start_coords, end_coords)
                        arrival_time = calculate_arrival_time(f[4], duration) if duration else "N/A"
                        
                        st.markdown(f"""
                        <p style='color: black; margin-bottom: 8px;'><strong style='color: black;'>Distance :</strong> {distance if distance else 'Non disponible'}</p>
                        <p style='color: black; margin-bottom: 8px;'><strong style='color: black;'>Durée estimée :</strong> {duration if duration else 'Non disponible'}</p>
                        <p style='color: black;'><strong style='color: black;'>Heure d'arrivée estimée :</strong> {arrival_time}</p>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("<p style='color: black;'>Impossible de calculer les informations d'itinéraire</p>", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)

                    # Boutons
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("Modifier", key=f"edit_ride_{f[0]}", use_container_width=True):
                            st.session_state.edit_ride = f[0]
                            st.rerun()
                    with col_btn2:
                        if st.button("Supprimer", key=f"delete_ride_{f[0]}", use_container_width=True):
                            with sqlite3.connect('priminsberg_rides.db') as conn:
                                c = conn.cursor()
                                c.execute("DELETE FROM rides WHERE id=?", (f[0],))
                                c.execute("DELETE FROM bookings WHERE ride_id=?", (f[0],))
                                conn.commit()
                            st.success("Trajet supprimé !")
                            st.rerun()
                
                with col_map:
                    if start_coords and end_coords:
                        m = folium.Map(
                            location=[(start_coords[0] + end_coords[0])/2, 
                            (start_coords[1] + end_coords[1])/2],
                            zoom_start=6
                        )
                        
                        folium.Marker(
                            location=start_coords,
                            popup=f"Départ: {f[1]}",
                            icon=folium.Icon(color='green')
                        ).add_to(m)
                        
                        folium.Marker(
                            location=end_coords,
                            popup=f"Arrivée: {f[2]}",
                            icon=folium.Icon(color='red')
                        ).add_to(m)
                        
                        try:
                            osrm_url = f"http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full&geometries=geojson"
                            response = requests.get(osrm_url)
                            route_data = response.json()
                            
                            if route_data.get('code') == 'Ok':
                                route_coords = [(coord[1], coord[0]) for coord in route_data['routes'][0]['geometry']['coordinates']]
                                folium.PolyLine(
                                    locations=route_coords,
                                    color='blue',
                                    weight=3,
                                    opacity=0.7
                                ).add_to(m)
                            else:
                                folium.PolyLine(
                                    locations=[start_coords, end_coords],
                                    color='blue',
                                    weight=2.5,
                                    opacity=1
                                ).add_to(m)
                        except:
                            folium.PolyLine(
                                locations=[start_coords, end_coords],
                                color='blue',
                                weight=2.5,
                                opacity=1
                            ).add_to(m)
                        
                        folium_static(m, width=750, height=350)
                    else:
                        st.warning("Impossible de géocoder une ou plusieurs adresses")
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
        st.info(translate("Aucun trajet réservable trouvé."))
    else:
        for r in rows:
            with st.expander(f"{r[2]} → {r[3]}, {r[4]} {r[5]}, {translate('Fournisseur')} : {r[1]}, {translate('Sièges')} : {r[6]}", expanded=False):
                st.markdown(f"""
                <div style='background-color: var(--light-gray); padding: 15px; border-radius: 10px;'>
                    <h4 style='color: var(--accent-red); margin-top: 0;'>{translate("Détails du trajet")}</h4>
                    <p><strong>{translate("Itinéraire")} :</strong> {r[2]} → {r[3]}</p>
                    <p><strong>{translate("Date")} :</strong> {r[4]}</p>
                    <p><strong>{translate("Heure")} :</strong> {r[5]}</p>
                    <p><strong>{translate("Sièges disponibles")} :</strong> {r[6]}</p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div style='background-color: var(--light-gray); padding: 15px; border-radius: 10px; margin-top: 10px;'>
                    <h4 style='color: var(--accent-red); margin-top: 0;'>{translate("Informations sur le conducteur")}</h4>
                """, unsafe_allow_html=True)
                st.write(f"**{translate('Conducteur')} :** {r[7]} {r[8]}")
                st.write(f"**{translate('Nom d\'utilisateur')} :** {r[1]}")
                st.write(f"**{translate('Email')} :** {r[9]}")
                st.write(f"**{translate('Téléphone')} :** {r[10]}")
                st.markdown("</div>", unsafe_allow_html=True)

                with sqlite3.connect('priminsberg_rides.db') as conn:
                    c = conn.cursor()
                    c.execute('''SELECT u.first_name, u.last_name, u.username, u.email, u.phone
                                FROM bookings b
                                JOIN users u ON b.user_id = u.id
                                WHERE b.ride_id=?
                             ''', (r[0],))
                    passengers = c.fetchall()

                st.markdown(f"""
                <div style='background-color: var(--light-gray); padding: 15px; border-radius: 10px; margin-top: 10px;'>
                    <h4 style='color: var(--accent-red); margin-top: 0;'>{translate("Passagers")}</h4>
                """, unsafe_allow_html=True)
                if not passengers:
                    st.write(translate("Pas encore de passagers pour ce trajet."))
                else:
                    for p in passengers:
                        st.write(f"- {p[0]} {p[1]} ({translate('Nom d\'utilisateur')} : {p[2]}) {translate('Téléphone')} : {p[4]}")
                st.markdown("</div>", unsafe_allow_html=True)

                if r[6] > 0:
                    if st.button(translate("Réserver le trajet"), key=f"book_ride_{r[0]}"):
                        with sqlite3.connect('priminsberg_rides.db') as conn:
                            c = conn.cursor()
                            c.execute("SELECT available_seats FROM rides WHERE id=?", (r[0],))
                            current_seats = c.fetchone()
                            if not current_seats or current_seats[0] <= 0:
                                st.error(translate("Ce trajet n'est plus réservable ou n'a plus de sièges disponibles !"))
                                st.rerun()
                            else:
                                c.execute("INSERT INTO bookings (user_id, ride_id) VALUES (?, ?)",
                                          (st.session_state.current_user[0], r[0]))
                                c.execute("UPDATE rides SET available_seats=available_seats-1 WHERE id=?", (r[0],))
                                conn.commit()
                                st.success(translate("Trajet réservé avec succès !"))
                                st.rerun()

    if st.button(translate("Retour au profil"), key="display_rides_back_button"):
        st.session_state.menu_selection = "profile"
        st.rerun()

def show_offer_ride():
    with st.form(key="offer_ride_form"):
        start_location = st.text_input(translate("Lieu de départ"), key="offer_start_location")
        destination = st.text_input(translate("Destination"), key="offer_destination")
        date_input = st.date_input(translate("Date"), min_value=date.today(), key="offer_date")
        time_input = st.time_input(translate("Heure"), key="offer_time")
        available_seats = st.number_input(translate("Sièges disponibles"), min_value=1, step=1, value=1, key="offer_available_seats")

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button(translate("Enregistrer le trajet"))
            if submitted:
                if not all([start_location, destination, date_input, time_input, available_seats]):
                    st.error(translate("Veuillez remplir tous les champs !"))
                else:
                    date_str = date_input.strftime("%d.%m.%Y")
                    time_str = time_input.strftime("%H:%M")

                    with sqlite3.connect('priminsberg_rides.db') as conn:
                        c = conn.cursor()
                        c.execute("INSERT INTO rides (provider_id, start_location, destination, date, time, available_seats) VALUES (?, ?, ?, ?, ?, ?)",
                                  (st.session_state.current_user[0], start_location, destination, date_str, time_str, available_seats))
                        conn.commit()
                    st.success(translate("Trajet créé avec succès !"))
                    st.rerun()
        with col2:
            if st.form_submit_button(translate("Retour au profil")):
                st.session_state.menu_selection = "profile"
                st.rerun()
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


