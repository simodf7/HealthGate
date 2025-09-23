from utils.routes import register_routes
from utils.global_vars import *
from utils.config import app


# Registra le rotte
register_routes(app)

# Avvia il server Flask
if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)  # Avvia il server Flask in modalità debug
