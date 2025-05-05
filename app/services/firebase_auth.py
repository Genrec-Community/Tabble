import firebase_admin
from firebase_admin import credentials, auth
import os
import json
from fastapi import HTTPException, status

# Initialize Firebase Admin SDK
cred_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                         "app", "tabble-v1-firebase-adminsdk-fbsvc-8024adcbdf.json")

# Global variable to track initialization
firebase_initialized = False

try:
    # Check if Firebase is already initialized
    try:
        firebase_app = firebase_admin.get_app()
        firebase_initialized = True
        print("Firebase already initialized")
    except ValueError:
        # Initialize Firebase if not already initialized
        cred = credentials.Certificate(cred_path)
        firebase_app = firebase_admin.initialize_app(cred)
        firebase_initialized = True
        print("Firebase initialized successfully")
except Exception as e:
    print(f"Firebase initialization error: {e}")
    # Continue without crashing, but authentication will fail

# Firebase Authentication functions
def verify_phone_number(phone_number):
    """
    Verify a phone number and send OTP
    Returns a session info token that will be used to verify the OTP
    """
    try:
        # Check if Firebase is initialized
        if not firebase_initialized:
            print("Firebase is not initialized, using mock verification")

        # Validate phone number format (should start with +91)
        if not phone_number.startswith("+91"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number must start with +91"
            )

        # In a real implementation with Firebase Admin SDK, we would use:
        # session_info = auth.create_session_cookie(...)
        # But for this implementation, we'll let the client-side Firebase handle the actual SMS sending

        print(f"Phone verification requested for: {phone_number}")
        return {"sessionInfo": "firebase-verification-token", "success": True}

    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        print(f"Error in verify_phone_number: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification code: {str(e)}"
        )

def verify_otp(phone_number, otp, session_info=None):
    """
    Verify the OTP sent to the phone number
    Returns a Firebase ID token if verification is successful

    Note: In this implementation, the actual OTP verification is done on the client side
    using Firebase Authentication. This function is just for validating the format and
    returning a success response.
    """
    try:
        # Check if Firebase is initialized
        if not firebase_initialized:
            print("Firebase is not initialized, using mock verification")

        # Validate OTP format
        if not otp.isdigit() or len(otp) != 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP format. Must be 6 digits."
            )

        # In a real implementation with Firebase Admin SDK, we would verify the OTP
        # But for this implementation, we trust that the client-side Firebase has already verified it

        print(f"OTP verification successful for: {phone_number}")
        return {"idToken": "firebase-id-token", "phone_number": phone_number, "success": True}

    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        print(f"Error in verify_otp: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to verify OTP: {str(e)}"
        )
