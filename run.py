#!/usr/local/bin/python3
from app import app, db
from flask import Flask

app.run(debug=True, host='0.0.0.0')

'''
if __name__ == '__main__':
    manager.run()
'''
