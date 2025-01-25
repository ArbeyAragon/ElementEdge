import firebase_admin
from firebase_admin import credentials, firestore
import cv2
import base64
import numpy as np
from datetime import datetime, timedelta
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

# Captura una foto desde la cámara
def capture_image():
    try:
        cap = cv2.VideoCapture(0)  # Usa la cámara predeterminada
        if not cap.isOpened():
            print("Error: Could not access the camera.")
            return None

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame from the camera.")
                break

            _, buffer = cv2.imencode('.jpg', frame)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            yield image_base64

        cap.release()
    except Exception as e:
        print(f"Error capturing image: {e}")
        yield None

# Escribe datos en Firestore
def write_to_firestore(db, collection_name, document_id, data):
    try:
        doc_ref = db.collection(collection_name).document(document_id)
        doc_ref.set(data)
        print(f"Document {document_id} written successfully in collection {collection_name}.")
    except Exception as e:
        print(f"Error writing to Firestore: {e}")

if __name__ == "__main__":
    # Cambia el path por el archivo de tu clave de servicio
    service_account_key_path = "serviceAccountKey.json"
    db = initialize_firestore(service_account_key_path)

    if db:
        try:
            print("Capturing images every 3 seconds for 5 minutes. Press 'q' to stop early.")
            image_generator = capture_image()
            start_time = datetime.now()
            end_time = start_time + timedelta(minutes=5)

            for image_base64 in image_generator:
                if datetime.now() >= end_time:
                    print("5 minutes have passed. Stopping image capture.")
                    break

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Stopping image capture by user request.")
                    break

                if image_base64:
                    # Genera un ID único basado en el tiempo actual
                    document_id = f"image_{datetime.now().strftime('%Y%m%d%H%M%S')}"

                    # Datos a guardar
                    data = {
                        "timestamp": datetime.now().isoformat(),
                        "image_base64": image_base64
                    }

                    # Escribe en Firestore
                    collection_name = "images"
                    write_to_firestore(db, collection_name, document_id, data)

                time.sleep(3)  # Espera 3 segundos antes de capturar la siguiente imagen
        except KeyboardInterrupt:
            print("Image capture stopped by user.")
        finally:
            cv2.destroyAllWindows()
