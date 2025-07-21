import streamlit as st
import sqlite3
import bcrypt
import datetime
from datetime import date
from PIL import Image
import os
import base64
from Database_Fahrten import setup_db
from Utils_Fahrten import display_logo,hash_password,verify_password,translate,get_base64_icon,styled_subheader







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
    elif st.button("Retour au profil/Zurück zum Profil", key="my_rides_back_button"):
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


