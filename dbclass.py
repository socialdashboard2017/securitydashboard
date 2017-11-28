from flask import Flask, request, flash, url_for, redirect, render_template, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from sqlalchemy import exists
import telegrambot
import scoring_functions

app = Flask(__name__)

app.config.from_object('config.BaseConfig')

db = SQLAlchemy(app)