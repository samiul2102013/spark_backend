from django.conf import settings
from firebase_admin import auth as firebase_auth, initialize_app, get_app


def _get_firebase_app():
    try:
        return get_app()
    except ValueError:
        return initialize_app()


class FirebaseTokenVerifier:

    def verify(self, id_token: str) -> dict:
        try:
            app = _get_firebase_app()
            decoded = firebase_auth.verify_id_token(id_token, app=app)
            return decoded
        except firebase_auth.ExpiredIdTokenError:
            raise ValueError("Firebase ID token has expired.")
        except firebase_auth.RevokedIdTokenError:
            raise ValueError("Firebase ID token has been revoked.")
        except firebase_auth.InvalidIdTokenError:
            raise ValueError("Firebase ID token is invalid.")
        except Exception as e:
            raise ValueError(f"Firebase token verification failed: {e}")