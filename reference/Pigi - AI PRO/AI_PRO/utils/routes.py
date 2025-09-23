from flask import jsonify, request, render_template, redirect, url_for, session, current_app, Response
import jwt
import requests
import time
from utils.video_stream import generate_video_stream
import utils.global_vars
from utils.config import keycloak

def register_routes(app):
    @app.route('/set_target_reps', methods=['POST'])
    def set_target_reps():
        data = request.get_json()  # Ottieni i dati inviati tramite POST
        count_max = data.get('target_reps', 10)  # Imposta il massimo delle ripetizioni
        utils.global_vars.target_repetitions = count_max  # Aggiorna la variabile globale
        return jsonify({"status": "success", "target_reps": count_max})  # Risposta JSON

    @app.route('/workout_history')
    def get_workout_history():
        return jsonify(utils.global_vars.workout_history)  # Ritorna lo storico come JSON

    @app.route('/exercise_data')
    def exercise_data():
        rest_remaining = max(0, utils.global_vars.rest_duration - (time.time() - utils.global_vars.rest_start_time)) if utils.global_vars.resting else 0
        return jsonify({
            'reps': utils.global_vars.current_reps, 
            'exercise': utils.global_vars.current_exercise,
            'target_reps': utils.global_vars.target_repetitions,
            'workout_history': utils.global_vars.workout_history,
            'resting': utils.global_vars.resting,
            'rest_remaining': rest_remaining,
            'start_timer': utils.global_vars.start_timer  # Aggiungi il timer di avvio
        })

    @app.route('/')
    def index():
        if 'keycloak_token' in session:  # Verifica se c'è un token nella sessione
            token = session['keycloak_token']  # Prendi l'access token

            print(token)

            try:
                # Decodifica il token senza verificare la firma
                decoded_token = jwt.decode(token['access_token'], options={"verify_signature": False}, algorithms=["RS256"])

                # Ottieni i ruoli direttamente dal decoded_token
                roles = decoded_token.get('realm_access', {}).get('roles', [])

                # Ottieni le informazioni utente
                response = keycloak.get(
                    'http://localhost:8080/realms/Realm1/protocol/openid-connect/userinfo',
                    token=token
                )

                user_info = response.json()
                user_info['roles'] = roles  # Aggiungi i ruoli alle informazioni utente

                return render_template('index.html', user_info=user_info)  # Renderizza la pagina con le informazioni utente
            except Exception as e:
                return render_template('error.html', error=str(e))  # Mostra un errore se qualcosa va storto
        return render_template('login.html')  # Mostra la pagina di login se non autenticato

    @app.route('/login')
    def login():
        redirect_uri = url_for('auth', _external=True)  # URI di reindirizzamento per Keycloak
        return keycloak.authorize_redirect(redirect_uri, prompt='login')  # Redirige alla pagina di login di Keycloak

    @app.route('/auth')
    def auth():
        try:
            token = keycloak.authorize_access_token()  # Ottiene il token da Keycloak
            session['keycloak_token'] = token  # Salva il token nella sessione
            return redirect(url_for('index'))  # Redirige alla home
        except Exception as e:
            current_app.logger.error(f"Error authorizing access token: {str(e)}")  # Logga l'errore
            return render_template('error.html', error=f"Error authorizing access token: {str(e)}")  # Mostra un messaggio di errore

    @app.route('/logout')
    def logout():
        token = session.get('keycloak_token')  # Prendi il token dalla sessione
        if token:
            id_token = token.get('id_token')  # Ottieni l'id_token
            logout_url = 'http://localhost:8080/realms/Realm1/protocol/openid-connect/logout'  # URL di logout di Keycloak
            params = {
                'id_token': id_token,
                'client_id': 'Client1',
                'post_logout_redirect_uri': 'http://localhost:5000/'  # URL di reindirizzamento post-logout
            }
            try:
                response = requests.post(logout_url, data=params)  # Effettua la richiesta di logout
                if response.status_code == 200:
                    current_app.logger.info('Successfully logged out from Keycloak.')  # Logga il successo
                else:
                    current_app.logger.error(f"Keycloak logout failed: {response.status_code} - {response.text}")  # Logga eventuali errori
            except Exception as e:
                current_app.logger.error(f"Error contacting Keycloak logout endpoint: {e}")  # Logga l'errore di connessione
            session.clear()  # Cancella la sessione Flask
        return redirect(url_for('index'))  # Redirige alla home

    @app.route('/allenamento')
    def allenamento():
        if 'keycloak_token' in session:
            token = session['keycloak_token']
            try:
                # Decodifica il token senza verificare la firma
                decoded_token = jwt.decode(token['access_token'], options={"verify_signature": False}, algorithms=["RS256"])

                # Ottieni i ruoli direttamente dal decoded_token
                roles = decoded_token.get('realm_access', {}).get('roles', [])

                # Ottieni le informazioni utente
                response = keycloak.get(
                    'http://localhost:8080/realms/Realm1/protocol/openid-connect/userinfo',
                    token=token
                )

                user_info = response.json()

                # Logica per la dashboard admin
                if 'userRole' in roles:
                    return render_template('allenamento.html')
                else:
                    return redirect(url_for('index'))
                
            except Exception as e:
                # Log: errore durante il tentativo di recupero dei dati
                current_app.logger.error(f"Errore durante l'accesso alla pagina di allanamento: {str(e)}")
                return render_template('error.html', error=str(e))
        else:
            return redirect(url_for('index'))

    @app.route('/dashboard')
    def dashboard():
        if 'keycloak_token' in session:
            token = session['keycloak_token']
            try:
                # Decodifica il token senza verificare la firma
                decoded_token = jwt.decode(token['access_token'], options={"verify_signature": False}, algorithms=["RS256"])

                # Ottieni i ruoli direttamente dal decoded_token
                roles = decoded_token.get('realm_access', {}).get('roles', [])

                # Ottieni le informazioni utente
                response = keycloak.get(
                    'http://localhost:8080/realms/Realm1/protocol/openid-connect/userinfo',
                    token=token
                )

                user_info = response.json()

                # Logica per la dashboard admin
                if 'adminRole' in roles:
                    return render_template('dashboard.html')
                else:
                    return redirect(url_for('index'))
                
            except Exception as e:
                # Log: errore durante il tentativo di recupero dei dati
                current_app.logger.error(f"Errore durante l'accesso al pannello di amministrazione: {str(e)}")
                return render_template('error.html', error=str(e))
        else:
            return redirect(url_for('index'))

    @app.route('/video_feed')
    def video_feed():
        return Response(generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')  # Ritorna il video stream

    @app.route('/reset_workout_history', methods=['POST'])
    def reset_workout_history():

        # Resetta le variabili globali
        utils.global_vars.workout_history = {}
        utils.global_vars.count = 0
        utils.global_vars.stage = None
        utils.global_vars.resting = False
        utils.global_vars.rest_start_time = 0
        utils.global_vars.exercise_recognized = False
        utils.global_vars.current_exercise = "Not recognized"
        utils.global_vars.current_reps = 0
        utils.global_vars.count_max = 0
        utils.global_vars.start_timer = 5

        return jsonify({"status": "success", "message": "Workout history reset"})  # Ritorna una risposta JSON

    @app.route('/log_error', methods=['POST'])
    def log_error():
        data = request.get_json()  # Prendi i dati JSON inviati
        error_message = data.get('error')  # Estrai il messaggio di errore
        if error_message:
            current_app.logger.error(error_message)  # Logga l'errore
            return jsonify({"status": "success", "message": "Error logged"}), 200  # Risposta di successo
        else:
            return jsonify({"status": "error", "message": "No error message provided"}), 400  # Risposta di errore
