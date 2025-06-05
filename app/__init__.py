import sqlite3
import os

from flask import Flask, render_template, redirect, request, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from jinja2 import TemplateNotFound
from werkzeug.security import check_password_hash
from .models import get_user_by_username, get_user_by_id_with_role, get_role_page_permissions_from_db
from .utils import page_name_map

# routes
from .role_routes import role_bp
from .account_routes import account_bp
from .power_routes import power_bp
from .water_routes import water_bp
from .taiwater_power_routes import taiwater_power_bp

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'supersecretkey'

    login_manager.init_app(app)
    login_manager.login_view = 'login'
    app.register_blueprint(role_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(power_bp)
    app.register_blueprint(water_bp)
    app.register_blueprint(taiwater_power_bp)

    class User(UserMixin):
        def __init__(self, id, username, full_name, phone, district_id, district, village, role_id, role_name):
            self.id = id
            self.username = username
            self.full_name = full_name
            self.phone = phone
            self.district_id = district_id
            self.district = district
            self.village = village
            self.role_id = role_id
            self.role_name = role_name

    @login_manager.user_loader
    def load_user(user_id):
        user = get_user_by_id_with_role(user_id)
        if user:
            return User(
                user['id'], user['username'], user['full_name'], user['phone'],
                user['district_id'], user['district'], user['village'], user['role_id'], user['role_name']
            )
        return None

    @app.route('/', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = get_user_by_username(username)
            if user and check_password_hash(user['password'], password):
                login_user(User(
                    user['id'], user['username'], user['full_name'], user['phone'],
                    user['district_id'], user['district'], user['village'], user['role_id'], user['role_name']
                ))
                return redirect(url_for('page_info', page='profile'))
            else:
                flash("Invalid credentials", "danger")
        return render_template('login.html')

    @app.route('/dashboard')
    @login_required
    def dashboard():
        return f"Hello {current_user.full_name}, you're logged in with role name {current_user.role_name}."

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    # @app.route('/page/<page>')
    # @login_required
    # def page_info(page):
    #     all_permissions = get_role_page_permissions_from_db()
    #     role_name = current_user.role_name
    #     role_pages = all_permissions.get(role_name, {})
    #     actions = role_pages.get(page, [])
    #     return render_template('page_info.html',
    #                         role=role_name,
    #                         current_page=page,
    #                         actions=actions,
    #                         pages=role_pages,
    #                         page_name_map=page_name_map)

    @app.route('/page/<page>')
    @login_required
    def page_info(page):
        all_permissions = get_role_page_permissions_from_db()
        role_name = current_user.role_name
        role_pages = all_permissions.get(role_name, {})
        actions = role_pages.get(page, [])

        # 將通用變數整理
        context = {
            "role": role_name,
            "current_page": page,
            "current_page_name": page_name_map.get(page, page),
            "actions": actions,
            "pages": role_pages,
            "page_name_map": page_name_map,
            "user_permissions": actions  # 傳入模板供判斷權限
        }

        # 預設檢查該頁面是否有對應模板
        target_template = f"{page}.html"

        try:
            return render_template(target_template, **context)
        except TemplateNotFound:
            return render_template("page_info.html", **context)

    return app

if __name__ == "__main__":
    app.run(debug=True)
