import streamlit as st
import sqlite3
import bcrypt
import datetime
from datetime import date, datetime
from PIL import Image
import os
import base64
import sqlite3
import bcrypt
import datetime
from datetime import date, datetime
from PIL import Image
import os
import base64 
from Utils_Fahrten import get_user_by_username_db
DB_FILE = 'priminsberg_rides.db'
UPLOAD_DIR = "uploads" # Base directory for all uploaded files
PROFILE_PICTURES_DIR = os.path.join(UPLOAD_DIR, "profile_pictures")
VEHICLE_PICTURES_DIR = os.path.join(UPLOAD_DIR, "vehicle_pictures")

# Create directories if they don't exist
os.makedirs(PROFILE_PICTURES_DIR, exist_ok=True)
os.makedirs(VEHICLE_PICTURES_DIR, exist_ok=True)

def save_vehicle_image(uploaded_file, user_id, image_type):
    """
    Saves a vehicle image to the specified directory and returns its relative path.
    Args:
        uploaded_file: The file object uploaded via Streamlit.
        user_id: The ID of the user owning the vehicle.
        image_type: A string indicating the type of image (e.g., 'inter1', 'exter1').
    Returns:
        The relative path to the saved image, or None if saving fails.
    """
    if not uploaded_file:
        return None
    
    # Ensure the target directory exists
    os.makedirs(VEHICLE_PICTURES_DIR, exist_ok=True)
    
    # Generate a unique filename to prevent overwrites
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    # Using timestamp for uniqueness
    filename = f"vehicle_{user_id}_{image_type}_{int(datetime.now().timestamp())}{file_ext}"
    filepath = os.path.join(VEHICLE_PICTURES_DIR, filename)
    
    # Save the image file
    try:
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        # Return path relative to UPLOAD_DIR for database storage
        return os.path.join(os.path.basename(VEHICLE_PICTURES_DIR), filename)
    except Exception as e:
        print(f"Error saving vehicle image: {e}")
        return None

def save_profile_picture(uploaded_file, user_id):
    """
    Saves a user's profile picture and returns its relative path.
    Args:
        uploaded_file: The file object uploaded via Streamlit.
        user_id: The ID of the user.
    Returns:
        The relative path to the saved image, or None if saving fails.
    """
    if not uploaded_file:
        return None
    
    # Ensure the target directory exists
    os.makedirs(PROFILE_PICTURES_DIR, exist_ok=True)
    
    # Generate a unique filename for the profile picture
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    # Profile pictures often replace previous ones, so a fixed name per user might be desired,
    # but using timestamp for uniqueness here to match vehicle image logic.
    filename = f"profile_{user_id}_{int(datetime.now().timestamp())}{file_ext}"
    filepath = os.path.join(PROFILE_PICTURES_DIR, filename)
    
    # Save the image file
    try:
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        # Return path relative to UPLOAD_DIR for database storage
        return os.path.join(os.path.basename(PROFILE_PICTURES_DIR), filename)
    except Exception as e:
        print(f"Error saving profile picture: {e}")
        return None

def save_image(uploaded_file, directory, prefix):
    """
    Generic function to save an image file to a specified directory.
    This function is more general and can be used for various image types.
    Args:
        uploaded_file: The file object uploaded via Streamlit.
        directory: The full path to the directory where the image should be saved.
        prefix: A string prefix for the filename.
    Returns:
        The relative path (from UPLOAD_DIR) to the saved image, or None if saving fails.
    Raises:
        ValueError: If the file format is not supported.
    """
    if not uploaded_file:
        return None
    
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    if file_ext not in ['.jpg', '.jpeg', '.png']:
        raise ValueError("Unsupported image format. Only .jpg, .jpeg, .png are allowed.")
    
    # Ensure the target directory exists
    os.makedirs(directory, exist_ok=True)
    
    filename = f"{prefix}_{int(datetime.now().timestamp())}{file_ext}"
    filepath = os.path.join(directory, filename)
    
    # Resize and save the image
    try:
        img = Image.open(uploaded_file)
        img.thumbnail((800, 800)) # Resize for efficiency and consistency
        img.save(filepath)
        # Return path relative to UPLOAD_DIR for database storage
        # This assumes 'directory' is a subdirectory of UPLOAD_DIR
        relative_path_from_upload = os.path.relpath(filepath, UPLOAD_DIR)
        return relative_path_from_upload
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

def setup_db():
    """
    Configures the SQLite database, creating tables and adding columns if they don't exist.
    Handles tables for users, rides, bookings, and vehicles, including image paths.
    """
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()

        # Table users with profile_picture
        c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            station TEXT,
            email TEXT,
            phone TEXT,
            driving_license_date TEXT,
            profile_picture TEXT -- Path to the profile picture
        )''')

        # Add columns if they don't exist (for backward compatibility)
        # This loop is generally good for adding new columns to existing databases
        for column in ['driving_license_date', 'profile_picture']:
            try:
                c.execute(f'ALTER TABLE users ADD COLUMN {column} TEXT')
            except sqlite3.OperationalError as e:
                # Ignore "duplicate column name" errors
                if "duplicate column name" not in str(e):
                    print(f"Error adding column {column} to users table: {e}")

        # Table rides
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
        )''')

        # Table bookings
        c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ride_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(ride_id) REFERENCES rides(id)
        )''')

        # Table vehicul with image paths
        c.execute('''
        CREATE TABLE IF NOT EXISTS vehicul (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            marque TEXT,
            model TEXT,
            date_mise_en_circulation TEXT,
            picture_inter1 TEXT, -- Path to interior picture 1
            picture_inter2 TEXT, -- Path to interior picture 2
            picture_exter1 TEXT, -- Path to exterior picture 1
            picture_exter2 TEXT, -- Path to exterior picture 2
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )''')
        conn.commit()

# --- User Management Functions ---

def register_user_db(username, password_hash, first_name, last_name, station, email, phone, driving_license_date=None, profile_picture=None):
    """
    Registers a new user with an optional profile picture.
    Returns the new user's ID or None if the username already exists.
    """
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO users (username, password, first_name, last_name, station, email, phone, driving_license_date, profile_picture) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, first_name, last_name, station, email, phone, driving_license_date, profile_picture))
            conn.commit()
            return c.lastrowid
        except sqlite3.IntegrityError:
            # Username already exists
            return None



def update_user_profile_db(user_id, first_name, last_name, station, email, phone, driving_license_date=None):
    """
    Updates a user's profile information (excluding profile picture).
    Returns True on success.
    """
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            UPDATE users SET first_name=?, last_name=?, station=?, email=?, phone=?, driving_license_date=? 
            WHERE id=?
        ''', (first_name, last_name, station, email, phone, driving_license_date, user_id))
        conn.commit()
        return True

def update_user_profile_picture(user_id, image_path):
    """
    Updates only the profile picture path for a user.
    Deletes the old picture file if it exists.
    Returns True on success.
    """
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        # Retrieve the old image path to delete the file
        c.execute("SELECT profile_picture FROM users WHERE id=?", (user_id,))
        old_image_path = c.fetchone()[0] # Get the path string

        if old_image_path:
            delete_image(old_image_path) # Call delete_image with the relative path
        
        # Update with the new image path
        c.execute("UPDATE users SET profile_picture=? WHERE id=?", (image_path, user_id))
        conn.commit()
        return True

# --- Ride Management Functions ---

def add_ride_db(provider_id, start_location, destination, date, time, available_seats):
    """Adds a new ride to the database."""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO rides (provider_id, start_location, destination, date, time, available_seats) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (provider_id, start_location, destination, date, time, available_seats))
        conn.commit()
        return c.lastrowid

def get_rides_db():
    """Retrieves all available rides, joining with user information."""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            SELECT r.id, u.username, r.start_location, r.destination, r.date, r.time, r.available_seats 
            FROM rides r JOIN users u ON r.provider_id = u.id
            ORDER BY r.date, r.time
        ''')
        return c.fetchall()

def delete_ride_db(ride_id):
    """Deletes a ride from the database."""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM rides WHERE id=?", (ride_id,))
        conn.commit()
        return c.rowcount > 0

def update_ride_db(ride_id, start_location, destination, date, time, available_seats):
    """Updates an existing ride's details."""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            UPDATE rides SET start_location=?, destination=?, date=?, time=?, available_seats=?
            WHERE id=?
        ''', (start_location, destination, date, time, available_seats, ride_id))
        conn.commit()
        return c.rowcount > 0

# --- Booking Management Functions ---

def book_ride_db(user_id, ride_id):
    """
    Books a ride for a user, decrementing available seats.
    Returns True on successful booking, False otherwise (e.g., no seats).
    """
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT available_seats FROM rides WHERE id=?", (ride_id,))
        current_seats = c.fetchone()
        
        if current_seats and current_seats[0] > 0:
            # Check if user has already booked this ride to prevent duplicate bookings
            c.execute("SELECT COUNT(*) FROM bookings WHERE user_id=? AND ride_id=?", (user_id, ride_id))
            if c.fetchone()[0] > 0:
                print(f"User {user_id} has already booked ride {ride_id}.")
                return False # User already booked this ride

            c.execute("INSERT INTO bookings (user_id, ride_id) VALUES (?, ?)", (user_id, ride_id))
            c.execute("UPDATE rides SET available_seats=? WHERE id=?", (current_seats[0] - 1, ride_id))
            conn.commit()
            return True
        return False # No seats available or ride not found

def get_user_bookings_db(user_id):
    """
    Retrieves all bookings made by a specific user.
    Returns a list of tuples containing ride details.
    """
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            SELECT r.id, u_provider.username, r.start_location, r.destination, r.date, r.time, r.available_seats
            FROM bookings b
            JOIN rides r ON b.ride_id = r.id
            JOIN users u_provider ON r.provider_id = u_provider.id
            WHERE b.user_id = ?
            ORDER BY r.date, r.time
        ''', (user_id,))
        return c.fetchall()

# --- Vehicle Management Functions ---

def add_vehicul_db(user_id, marque, model, date_mise_en_circulation, pictures=None):
    """
    Adds a new vehicle for a user with optional image paths.
    Args:
        user_id: The ID of the user owning the vehicle.
        marque: Vehicle make.
        model: Vehicle model.
        date_mise_en_circulation: Date of first registration.
        pictures: A dictionary containing image paths (e.g., {'inter1': 'path/to/img.jpg'}).
    Returns:
        The ID of the newly added vehicle.
    """
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        # Ensure 'pictures' is a dictionary to safely use .get()
        pictures = pictures if pictures is not None else {}
        c.execute('''
            INSERT INTO vehicul (
                user_id, marque, model, date_mise_en_circulation,
                picture_inter1, picture_inter2, picture_exter1, picture_exter2
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, marque, model, date_mise_en_circulation,
            pictures.get('inter1'),
            pictures.get('inter2'),
            pictures.get('exter1'),
            pictures.get('exter2')
        ))
        conn.commit()
        return c.lastrowid

def get_user_vehiculs_db(user_id):
    """
    Retrieves all vehicles associated with a specific user.
    Returns a list of tuples containing vehicle details and image paths.
    """
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            SELECT id, marque, model, date_mise_en_circulation,
                   picture_inter1, picture_inter2, picture_exter1, picture_exter2
            FROM vehicul WHERE user_id = ?
        ''', (user_id,))
        return c.fetchall()

def update_vehicul_pictures(vehicle_id, pictures):
    """
    Updates the image paths for a specific vehicle.
    Deletes old image files before updating with new ones.
    Args:
        vehicle_id: The ID of the vehicle to update.
        pictures: A dictionary containing new image paths.
    Returns:
        True on success, False otherwise.
    """
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        # Retrieve the old image paths to delete the files
        c.execute('''
            SELECT picture_inter1, picture_inter2, picture_exter1, picture_exter2
            FROM vehicul WHERE id=?
        ''', (vehicle_id,))
        old_pics = c.fetchone()
        
        if old_pics: # Ensure old_pics is not None
            for pic_path in old_pics:
                if pic_path: # Only attempt to delete if path exists
                    delete_image(pic_path)
        
        # Update with the new image paths
        # Ensure 'pictures' is a dictionary to safely use .get()
        pictures = pictures if pictures is not None else {}
        c.execute('''
            UPDATE vehicul SET
                picture_inter1=?,
                picture_inter2=?,
                picture_exter1=?,
                picture_exter2=?
            WHERE id=?
        ''', (
            pictures.get('inter1'),
            pictures.get('inter2'),
            pictures.get('exter1'),
            pictures.get('exter2'),
            vehicle_id
        ))
        conn.commit()
        return c.rowcount > 0

def delete_image(image_path):
    """
    Deletes an image file from the file system.
    Args:
        image_path: The relative path to the image file (e.g., "profile_pictures/my_pic.jpg").
    Returns:
        True if the image was successfully deleted, False otherwise.
    """
    # Construct the full path to the image file
    full_image_path = os.path.join(UPLOAD_DIR, image_path)
    if image_path and os.path.exists(full_image_path):
        try:
            os.remove(full_image_path)
            print(f"Successfully deleted image: {full_image_path}")
            return True
        except Exception as e:
            print(f"Error deleting image {full_image_path}: {e}")
    else:
        print(f"Image not found or path is empty: {full_image_path}")
    return False

def display_image(image_path, width=None):
    """
    Displays an image in Streamlit from a relative path.
    Args:
        image_path: The relative path to the image (e.g., "profile_pictures/my_pic.jpg").
        width: Optional width for displaying the image.
    """
    full_image_path = os.path.join(UPLOAD_DIR, image_path)
    if image_path and os.path.exists(full_image_path):
        st.image(full_image_path, width=width)
    else:
        st.warning(f"Image not available: {image_path}")

# Example usage for testing (this block runs only when the script is executed directly)
if __name__ == "__main__":
    print("--- Running Database_Fahrten.py tests ---")
    
    # Clean up for testing
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Removed existing database: {DB_FILE}")
    
    # Clean up upload directories for testing
    import shutil
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
        print(f"Removed existing upload directory: {UPLOAD_DIR}")
    
    # Initialize the database
    setup_db()
    print("Database and upload directories initialized successfully.")

    # Test user registration and profile picture saving
    print("\n--- Testing User Registration and Profile Picture ---")
    hashed_password = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Create a dummy image file for testing profile picture
    dummy_image_path = "test_profile_pic.png"
    Image.new('RGB', (60, 30), color = 'red').save(dummy_image_path)
    
    # Simulate an uploaded file
    class MockUploadedFile:
        def __init__(self, name, content):
            self.name = name
            self._content = content
        def getbuffer(self):
            return self._content
    
    with open(dummy_image_path, "rb") as f:
        mock_profile_file = MockUploadedFile(dummy_image_path, f.read())

    profile_pic_path = save_profile_picture(mock_profile_file, 1) # user_id 1 for test
    print(f"Saved profile picture path: {profile_pic_path}")

    user_id = register_user_db("testuser", hashed_password, "John", "Doe", "StationA", "john.doe@example.com", "1234567890", "2020-01-01", profile_pic_path)
    if user_id:
        print(f"User 'testuser' registered with ID: {user_id}")
    else:
        print("Failed to register user 'testuser' (username might exist).")

    user_info = get_user_by_username_db("testuser")
    if user_info:
        print(f"Retrieved user info: {user_info}")
        # In a real Streamlit app, you'd use st.image here
        # display_image(user_info[9], width=100) # user_info[9] is profile_picture
    else:
        print("User 'testuser' not found.")

    # Test updating profile picture
    print("\n--- Testing Profile Picture Update ---")
    dummy_image_path_new = "test_profile_pic_new.png"
    Image.new('RGB', (60, 30), color = 'blue').save(dummy_image_path_new)
    with open(dummy_image_path_new, "rb") as f:
        mock_profile_file_new = MockUploadedFile(dummy_image_path_new, f.read())
    
    new_profile_pic_path = save_profile_picture(mock_profile_file_new, user_id)
    if update_user_profile_picture(user_id, new_profile_pic_path):
        print(f"Profile picture updated for user {user_id} to: {new_profile_pic_path}")
        user_info_updated = get_user_by_username_db("testuser")
        print(f"Updated user info: {user_info_updated}")
    else:
        print("Failed to update profile picture.")

    # Test vehicle management and images
    print("\n--- Testing Vehicle Management and Images ---")
    # Create dummy images for vehicle
    dummy_inter1_path = "test_inter1.png"
    dummy_exter1_path = "test_exter1.png"
    Image.new('RGB', (100, 50), color = 'green').save(dummy_inter1_path)
    Image.new('RGB', (100, 50), color = 'yellow').save(dummy_exter1_path)

    with open(dummy_inter1_path, "rb") as f:
        mock_inter1_file = MockUploadedFile(dummy_inter1_path, f.read())
    with open(dummy_exter1_path, "rb") as f:
        mock_exter1_file = MockUploadedFile(dummy_exter1_path, f.read())

    vehicle_pics = {
        'inter1': save_vehicle_image(mock_inter1_file, user_id, 'inter1'),
        'exter1': save_vehicle_image(mock_exter1_file, user_id, 'exter1')
    }
    print(f"Saved vehicle picture paths: {vehicle_pics}")

    vehicle_id = add_vehicul_db(user_id, "Toyota", "Corolla", "2018-05-10", vehicle_pics)
    if vehicle_id:
        print(f"Vehicle added with ID: {vehicle_id}")
    else:
        print("Failed to add vehicle.")

    user_vehicles = get_user_vehiculs_db(user_id)
    if user_vehicles:
        print(f"User's vehicles: {user_vehicles}")
        # In a real Streamlit app, you'd use st.image here for each pic
        # display_image(user_vehicles[0][4], width=150) # picture_inter1
    else:
        print("No vehicles found for user.")

    # Test updating vehicle pictures
    print("\n--- Testing Vehicle Picture Update ---")
    dummy_inter1_path_new = "test_inter1_new.png"
    Image.new('RGB', (100, 50), color = 'purple').save(dummy_inter1_path_new)
    with open(dummy_inter1_path_new, "rb") as f:
        mock_inter1_file_new = MockUploadedFile(dummy_inter1_path_new, f.read())
    
    updated_vehicle_pics = {
        'inter1': save_vehicle_image(mock_inter1_file_new, user_id, 'inter1_updated'),
        'inter2': None, # Example: setting one to None
        'exter1': vehicle_pics['exter1'], # Keep existing exter1
        'exter2': None
    }
    if update_vehicul_pictures(vehicle_id, updated_vehicle_pics):
        print(f"Vehicle pictures updated for vehicle {vehicle_id}.")
        user_vehicles_updated = get_user_vehiculs_db(user_id)
        print(f"Updated vehicle info: {user_vehicles_updated}")
    else:
        print("Failed to update vehicle pictures.")

    # Clean up dummy image files created for testing
    if os.path.exists(dummy_image_path): os.remove(dummy_image_path)
    if os.path.exists(dummy_image_path_new): os.remove(dummy_image_path_new)
    if os.path.exists(dummy_inter1_path): os.remove(dummy_inter1_path)
    if os.path.exists(dummy_exter1_path): os.remove(dummy_exter1_path)
    if os.path.exists(dummy_inter1_path_new): os.remove(dummy_inter1_path_new)
    print("\n--- Testing complete. ---")