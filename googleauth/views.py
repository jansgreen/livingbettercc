from django.shortcuts import render, redirect
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests
import google.auth.transport.requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
from social_django.utils import psa

def google_login(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_FILE,
        scopes=['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email']
    )
    flow.redirect_uri = request.build_absolute_uri('/google/auth/callback/google-oauth2/') 
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    request.session['state'] = state
    return redirect(authorization_url)

@psa('social:complete')
def google_callback(request, backend):
    state = request.session.get('state')
    if not state:
        return redirect('login')

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_FILE,
        scopes=['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email'],
        state=state
    )

    flow.redirect_uri = request.build_absolute_uri(f'/google/auth/callback/{backend}/')
    authorization_response = request.build_absolute_uri()
    
    try:
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        request_session = requests.Request()
        id_info = id_token.verify_oauth2_token(credentials.id_token, request_session, settings.GOOGLE_CLIENT_ID)
        
        # Autenticar usuario con social-auth
        user = request.backend.do_auth(request.GET.get('code'))
        if user:
            login(request, user)
            return redirect('/classroom/')
    except Exception as e:
        print(f"Google Auth Error: {e}")
    
    return redirect('login')
