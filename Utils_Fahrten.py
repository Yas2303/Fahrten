

import streamlit as st
import sqlite3
import bcrypt
import datetime
from datetime import date
from PIL import Image
import os
import base64


DB_FILE = 'priminsberg_rides.db'
def get_user_by_username_db(username):
    """
    Retrieves user information by username.
    Returns a tuple of user data or None if not found.
    """
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            SELECT id, username, password, first_name, last_name, station, email, phone, driving_license_date, profile_picture 
            FROM users WHERE username = ?
        ''', (username,))
        return c.fetchone()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def hash_password(password):
    """Hashe le mot de passe en utilisant bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Vérifie si un mot de passe correspond à son hachage."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def translate(text):
    """
    Fonction de traduction placeholder.
    Pour une application multilingue réelle, vous utiliseriez un dictionnaire
    de traduction complet ou une bibliothèque i18n dédiée.
    """
    translations = {
        "Gestion des trajets Priminsberg": "Priminsberg Ride Management",
        "Connexion": "Login",
        "Inscription": "Register",
        "Bienvenue sur Priminsberg Ride": "Welcome to Priminsberg Ride",
        "Bienvenue": "Welcome",
        "Mon Profil": "My Profile",
        "Mes véhicules": "My Vehicles", # Nouvelle traduction
        "Fahrten anzeigen": "Show Rides",
        "Proposer un trajet": "Offer a Ride",
        "Mes trajets": "My Rides",
        "Modifier le profil": "Edit Profile",
        "Se déconnecter": "Logout",
        "Bienvenue sur la plateforme de covoiturage Priminsberg": "Welcome to the Priminsberg carpooling platform",
        "Connectez-vous ou inscrivez-vous pour accéder à toutes les fonctionnalités.": "Log in or register to access all features.",
        "Se connecter": "Login",
        "S'inscrire": "Register",
        "Nom d'utilisateur": "Username",
        "Mot de passe": "Password",
        "Retour": "Back",
        "Échec de la connexion ! Nom d'utilisateur ou mot de passe invalide.": "Login failed! Invalid username or password.",
        "Prénom": "First Name",
        "Nom de famille": "Last Name",
        "Gare": "Station",
        "Votre gare habituelle, ex : 'Hauptbahnhof'": "Your usual station, e.g., 'Hauptbahnhof'",
        "Email": "Email",
        "Téléphone": "Phone",
        "Date d'obtention du permis de conduire": "Driving License Date",
        "Date d'obtention du permis de conduire non renseignée.": "Driving license date not provided.", # Nouvelle traduction
        "Veuillez remplir tous les champs !": "Please fill in all fields!",
        "Inscription terminée !": "Registration complete!",
        "Ce nom d'utilisateur existe déjà !": "This username already exists!",
        "Informations de profil": "Profile Information",
        "Aucun champ ne peut être vide !": "No field can be empty!",
        "Profil mis à jour !": "Profile updated!",
        "Lieu de départ": "Start Location",
        "Destination": "Destination",
        "Date du trajet": "Ride Date",
        "Heure du trajet (ex: 14:30)": "Ride Time (e.g., 14:30)",
        "Nombre de places disponibles": "Available Seats",
        "Ajouter le trajet": "Add Ride",
        "Trajet ajouté avec succès!": "Ride added successfully!",
        "Trajets disponibles": "Available Rides",
        "De:": "From:",
        "À:": "To:",
        "Date:": "Date:",
        "Heure:": "Time:",
        "Places:": "Seats:",
        "Proposé par:": "Offered by:",
        "Réserver ce trajet": "Book this ride",
        "Impossible de réserver ce trajet (plus de places disponibles ou erreur).": "Cannot book this ride (no more seats available or error).",
        "Complet": "Full",
        "Aucun trajet disponible pour le moment.": "No rides available for now.",
        "Mes réservations": "My Bookings",
        "Trajet ID:": "Ride ID:",
        "Vous n'avez aucune réservation pour le moment.": "You have no bookings yet.",
        "Ajouter un nouveau véhicule": "Add a new vehicle", # Nouvelle traduction
        "Marque du véhicule": "Vehicle Make", # Nouvelle traduction
        "Modèle du véhicule": "Vehicle Model", # Nouvelle traduction
        "Date de mise en circulation": "Date of First Registration", # Nouvelle traduction
        "Pour les images, vous pouvez entrer des chemins de fichiers ou des noms pour référence.": "For images, you can enter file paths or names for reference.", # Nouvelle traduction
        "Image intérieure 1 (chemin/nom)": "Interior Image 1 (path/name)", # Nouvelle traduction
        "Image intérieure 2 (chemin/nom)": "Interior Image 2 (path/name)", # Nouvelle traduction
        "Image extérieure 1 (chemin/nom)": "Exterior Image 1 (path/name)", # Nouvelle traduction
        "Image extérieure 2 (chemin/nom)": "Exterior Image 2 (path/name)", # Nouvelle traduction
        "Ajouter le véhicule": "Add Vehicle", # Nouvelle traduction
        "Véhicule ajouté avec succès!": "Vehicle added successfully!", # Nouvelle traduction
        "Liste de mes véhicules": "List of my vehicles", # Nouvelle traduction
        "ID Véhicule:": "Vehicle ID:", # Nouvelle traduction
        "Marque:": "Make:", # Nouvelle traduction
        "Modèle:": "Model:", # Nouvelle traduction
        "Date de mise en circulation:": "Date of First Registration:", # Nouvelle traduction
        "Image intérieure 1:": "Interior Image 1:", # Nouvelle traduction
        "Image intérieure 2:": "Interior Image 2:", # Nouvelle traduction
        "Image extérieure 1:": "Exterior Image 1:", # Nouvelle traduction
        "Image extérieure 2:": "Exterior Image 2:", # Nouvelle traduction
        "Vous n'avez pas encore ajouté de véhicule.": "You have not added any vehicle yet.", # Nouvelle traduction
        "Enregistrer": "Save",
        "Annuler": "Cancel",
        "Modifier le trajet": "Edit Ride",
        "Supprimer le trajet": "Delete Ride",
        "Confirmer la suppression": "Confirm Deletion",
        "Annuler la suppression": "Cancel Deletion",
        "Êtes-vous sûr de vouloir supprimer ce trajet ?": "Are you sure you want to delete this ride?",
        "Trajet supprimé avec succès.": "Ride deleted successfully.",
        "Erreur lors de la suppression du trajet.": "Error deleting ride.",
        "Icône du site non trouvée. Assurez-vous que 'Images/Logo_MitFahrn.ico' existe.": "Site icon not found. Make sure 'Images/Logo_MitFahrn.ico' exists.",
        "Votre solution de covoiturage simple et efficace.": "Your simple and efficient carpooling solution.",
        "Veuillez remplir tous les champs obligatoires !": "Please fill in all required fields!",
        "Veuillez remplir au moins la marque, le modèle et la date de mise en circulation du véhicule.": "Please fill in at least the make, model, and date of first registration for the vehicle.",
        "ID Trajet:": "Ride ID:",
        "Lieu de départ:": "Departure Location:",
        "Places disponibles:": "Available Seats:",
        "à": "to",
        "le": "on",
        "Enregistrer les modifications": "Save Changes",
        "Trajet mis à jour avec succès!": "Ride updated successfully!",
        "Trajet non trouvé pour modification.": "Ride not found for editing.",
        "Erreur lors de la mise à jour du profil.": "Error updating profile."
    }
    return translations.get(text, text) # Retourne le texte original si non trouvé

def get_base64_icon(path):
    """Convertit un fichier icône en chaîne base64 pour l'utilisation dans st.set_page_config."""
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def display_logo(path, width=None):
    """Affiche un logo. Assurez-vous que le chemin de l'image est correct."""
    if os.path.exists(path):
        st.image(path, width=width)
    else:
        st.warning(translate(f"Logo non trouvé à : {path}"))

def styled_subheader(text):
    """Affiche un sous-titre stylisé avec des couleurs définies dans le CSS."""
    st.markdown(f"<h2 style='color: var(--accent-red); font-size: 1.8em; font-weight: bold;'>{text}</h2>", unsafe_allow_html=True)

def display_app_header(title):
    """Affiche l'en-tête principal de l'application avec un style personnalisé."""
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 30px; padding: 20px; background-color: var(--primary-dark); border-radius: 15px; box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.4);">
        <h1 style="color: var(--off-white); font-size: 2.5em; margin-bottom: 10px;">{title}</h1>
        <p style="color: var(--secondary-gray); font-size: 1.1em;">{translate("Votre solution de covoiturage simple et efficace.")}</p>
    </div>
    """, unsafe_allow_html=True)

def display_image_from_path(image_path, caption="", width=150):
    """
    Affiche une image à partir d'un chemin de fichier.
    Si le chemin est invalide ou l'image n'existe pas, affiche un texte alternatif.
    """
    if image_path and os.path.exists(image_path):
        try:
            st.image(image_path, caption=caption, width=width)
        except Exception:
            st.write(f"[{translate('Image non affichable')}: {os.path.basename(image_path)}]")
    else:
        st.info(f"[{translate('Aucune image')}: {caption}]")

# Dictionnaire de traduction bilingue
translations = {
    # Page titles
    "Gestion des trajets Priminsberg": "Gestion des trajets Priminsberg / Priminsberg Fahrtenverwaltung",
    "Bienvenue sur Priminsberg Ride": "Bienvenue sur Priminsberg Ride / Willkommen bei Priminsberg Ride",
    "Connexion": "Connexion / Anmeldung",
    "Inscription": "Inscription / Registrierung",
    "Mon Profil": "Mon Profil / Mein Profil",
    "Trajets disponibles": "Trajets disponibles / Verfügbare Fahrten",
    "Proposer un trajet": "Proposer un trajet / Fahrt anbieten",
    "Mes trajets": "Mes trajets / Meine Fahrten",
    "Modifier le profil": "Modifier le profil / Profil bearbeiten",
    
    # Common buttons
    "Se connecter": "Se connecter / Anmelden",
    "S'inscrire": "S'inscrire / Registrieren",
    "Se déconnecter": "Se déconnecter / Abmelden",
    "Retour": "Retour / Zurück",
    "Retour au profil": "Retour au profil / Zurück zum Profil",
    "Enregistrer": "Enregistrer / Speichern",
    "Annuler": "Annuler / Abbrechen",
    "Modifier": "Modifier / Bearbeiten",
    "Supprimer": "Supprimer / Löschen",
    
    # Form labels
    "Nom d'utilisateur": "Nom d'utilisateur / Benutzername",
    "Mot de passe": "Mot de passe / Passwort",
    "Prénom": "Prénom / Vorname",
    "Nom de famille": "Nom de famille / Nachname",
    "Gare": "Gare / Bahnhof",
    "Email": "Email / E-Mail",
    "Téléphone": "Téléphone / Telefon",
    "Lieu de départ": "Lieu de départ / Abfahrtsort",
    "Destination": "Destination / Ziel",
    "Date": "Date / Datum",
    "Heure": "Heure / Uhrzeit",
    "Sièges disponibles": "Sièges disponibles / Verfügbare Plätze",
    
    # Messages
    "Échec de la connexion ! Nom d'utilisateur ou mot de passe invalide.": 
        "Échec de la connexion ! Nom d'utilisateur ou mot de passe invalide. / Anmeldung fehlgeschlagen! Ungültiger Benutzername oder Passwort.",
    "Veuillez remplir tous les champs !": 
        "Veuillez remplir tous les champs ! / Bitte füllen Sie alle Felder aus!",
    "Ce nom d'utilisateur existe déjà !": 
        "Ce nom d'utilisateur existe déjà ! / Dieser Benutzername existiert bereits!",
    "Inscription terminée !": 
        "Inscription terminée ! / Registrierung abgeschlossen!",
    "Informations de profil": 
        "Informations de profil / Profilinformationen",
    "Aucun trajet réservable trouvé.": 
        "Aucun trajet réservable trouvé. / Keine buchbaren Fahrten gefunden.",
    "Détails du trajet": 
        "Détails du trajet / Fahrtdetails",
    "Itinéraire": 
        "Itinéraire / Route",
    "Conducteur": 
        "Conducteur / Fahrer",
    "Passagers": 
        "Passagers / Mitfahrer",
    "Pas encore de passagers pour ce trajet.": 
        "Pas encore de passagers pour ce trajet. / Noch keine Mitfahrer für diese Fahrt.",
    "Réserver le trajet": 
        "Réserver le trajet / Fahrt buchen",
    "Ce trajet n'est plus réservable ou n'a plus de sièges disponibles !": 
        "Ce trajet n'est plus réservable ou n'a plus de sièges disponibles ! / Diese Fahrt ist nicht mehr buchbar oder hat keine freien Plätze mehr!",
    "Trajet réservé avec succès !": 
        "Trajet réservé avec succès ! / Fahrt erfolgreich gebucht!",
    "Trajet créé avec succès !": 
        "Trajet créé avec succès ! / Fahrt erfolgreich erstellt!",
    "Réservation annulée !": 
        "Réservation annulée ! / Buchung storniert!",
    "Trajet supprimé !": 
        "Trajet supprimé ! / Fahrt gelöscht!",
    "Trajet mis à jour avec succès !": 
        "Trajet mis à jour avec succès ! / Fahrt erfolgreich aktualisiert!",
    "Le trajet n'existe plus !": 
        "Le trajet n'existe plus ! / Die Fahrt existiert nicht mehr!",
    "Aucun champ ne peut être vide !": 
        "Aucun champ ne peut être vide ! / Kein Feld darf leer sein!",
    "Profil mis à jour !": 
        "Profil mis à jour ! / Profil aktualisiert!",
    "Vous n'avez réservé aucun trajet.": 
        "Vous n'avez réservé aucun trajet. / Sie haben keine Fahrten gebucht.",
    "Vous n'avez proposé aucun de vos propres trajets.": 
        "Vous n'avez proposé aucun de vos propres trajets. / Sie haben keine eigenen Fahrten angeboten.",
    "Annuler la réservation": 
        "Annuler la réservation / Buchung stornieren",
    "Passagers sur ce trajet": 
        "Passagers sur ce trajet / Mitfahrer auf dieser Fahrt",
    
    # Landing page
    "Bienvenue sur la plateforme de covoiturage Priminsberg": 
        "Bienvenue sur la plateforme de covoiturage Priminsberg / Willkommen auf der Priminsberg Mitfahrplattform",
    "Connectez-vous ou inscrivez-vous pour accéder à toutes les fonctionnalités.": 
        "Connectez-vous ou inscrivez-vous pour accéder à toutes les fonctionnalités. / Melden Sie sich an oder registrieren Sie sich, um auf alle Funktionen zuzugreifen.",
    
    # Profile
    "Bienvenue": 
        "Bienvenue / Willkommen",
}

def translate(text):
    """Retourne la traduction bilingue du texte si disponible, sinon retourne le texte original"""
    return translations.get(text, text)

def get_base64_icon(image_path):
    try:
        full_path = os.path.join(os.path.dirname(__file__), image_path)
        with open(full_path, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        return encoded_string
    except FileNotFoundError:
        st.error(translate("Erreur : Fichier d'icône introuvable. Vérifiez le chemin."))
        return None
    except Exception as e:
        st.error(translate(f"Erreur lors du chargement de l'icône : {e}"))
        return None

def display_logo(image_path, width=300):
    try:
        full_path = os.path.join(os.path.dirname(__file__), image_path)
        img = Image.open(full_path)
        st.image(img, width=width)
    except FileNotFoundError:
        st.error(translate(f"Erreur : Image introuvable. Vérifiez le chemin."))
    except Exception as e:
        st.error(translate(f"Erreur lors du chargement de l'image : {e}"))


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verify_password(plain_password, hashed_password):

    return bcrypt.checkpw(plain_password.encode(), hashed_password)

