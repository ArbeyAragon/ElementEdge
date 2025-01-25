import firebase_admin
from firebase_admin import credentials, firestore
import cv2
import base64
import numpy as np
import time

# Inicializa la aplicación de Firebase Admin
def initialize_firestore(service_account_key_path):
    try:
        cred = credentials.Certificate(service_account_key_path)
        firebase_admin.initialize_app(cred)
        print("Firestore initialized successfully!")
        return firestore.client()
    except Exception as e:
        print(f"Error initializing Firestore: {e}")
        return None

# Lee el último documento de Firestore
def read_last_document(db, collection_name):
    try:
        docs = db.collection(collection_name).order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1).stream()
        for doc in docs:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"Error reading Firestore: {e}")
        return None

# Decodifica una imagen base64 y la muestra
def display_image_from_base64(image_base64):
    try:
        image_data = base64.b64decode(image_base64)
        np_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        if image is not None:
            cv2.imshow("Last Captured Image", image)
            cv2.waitKey(1)  # Actualiza la ventana sin pausar
        else:
            print("Error: Could not decode the image.")
    except Exception as e:
        print(f"Error displaying image: {e}")

if __name__ == "__main__":
    # Cambia el path por el archivo de tu clave de servicio
    service_account_key_path = "serviceAccountKey.json"
    db = initialize_firestore(service_account_key_path)

    if db:
        collection_name = "images"
        print("Displaying the latest image every 3 seconds. Press 'q' to stop.")

        try:
            while True:
                last_document = read_last_document(db, collection_name)

                if last_document and "image_base64" in last_document:
                    display_image_from_base64(last_document["image_base64"])
                else:
                    print("No valid image data found in the last document.")

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Exiting image display.")
                    break

                time.sleep(3)  # Espera 3 segundos antes de actualizar
        finally:
            cv2.destroyAllWindows()
