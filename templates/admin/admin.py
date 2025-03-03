from flask import Flask, Blueprint, render_template, url_for, redirect, request


admin_pg = Blueprint('admin', __name__, template_folder='templates/admin')

@admin_pg.route("/as")
def admin():
    return "Hello"