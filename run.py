from app import app
import os
import secrets

port = int(os.environ.get("PORT", 5000))
app.config['SECRET_KEY']=secrets.token_urlsafe(16)
app.run(debug=True, host="0.0.0.0", port=port)

