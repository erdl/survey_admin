#!/usr/bin/python3
from ubuntuStation import app, db
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app.run(debug=True, host='0.0.0.0', port=8989)
