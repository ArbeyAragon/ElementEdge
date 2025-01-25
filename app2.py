import firebase_admin
from firebase_admin import credentials, firestore

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

# Escribe datos en Firestore
def write_to_firestore(db, collection_name, document_id, data):
    try:
        doc_ref = db.collection(collection_name).document(document_id)
        doc_ref.set(data)
        print(f"Document {document_id} written successfully in collection {collection_name}.")
    except Exception as e:
        print(f"Error writing to Firestore: {e}")

# Lee datos de Firestore
def read_from_firestore(db, collection_name, document_id):
    try:
        doc_ref = db.collection(collection_name).document(document_id)
        doc = doc_ref.get()
        if doc.exists:
            print(f"Document {document_id} data: {doc.to_dict()}")
            return doc.to_dict()
        else:
            print(f"Document {document_id} does not exist in collection {collection_name}.")
            return None
    except Exception as e:
        print(f"Error reading from Firestore: {e}")
        return None

if __name__ == "__main__":
    # Cambia el path por el archivo de tu clave de servicio
    service_account_key_path = "serviceAccountKey.json"
    db = initialize_firestore(service_account_key_path)

    if db:
        # Ejemplo de escritura
        collection_name = "test_collection"
        document_id = "example_doc"
        data = {
            "name": "Arbey",
            "age": 30,
            "skills": ["Python", "Firestore", "Firebase"]
        }
        write_to_firestore(db, collection_name, document_id, data)

        # Ejemplo de lectura
        read_from_firestore(db, collection_name, document_id)
