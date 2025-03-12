from flask import Flask, Blueprint, render_template, url_for, redirect, request, flash, session
import hashlib
import psycopg2
from key import *
from datetime import datetime
now = datetime.now()


def init_db():
    conn = psycopg2.connect(
                    database=db_name,
                    host=host,
                    user=user_name,
                    password=pass_word,
                    port=5433)
    return conn

hivo = Blueprint('hivo', __name__, template_folder='templates')
SECRET_KEY = 'development'

@hivo.route("/")
def hivo_index():
    return render_template("hivo/dashboard.html")