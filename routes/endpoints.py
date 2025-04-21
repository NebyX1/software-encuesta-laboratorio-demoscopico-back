from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    jsonify,
    request,
    send_file,
)
from flask_login import (
    login_user,
    logout_user,
    login_required,
    LoginManager,
    current_user,
)
from helpers.forms import LoginForm, SurveyResponseForm
from database.models import User, ValidToken, SurveyResponse
from database.db import db
from jinja2 import TemplateNotFound
from sqlalchemy import func, desc
from io import BytesIO, StringIO
import csv
import json
from datetime import datetime

login_manager = LoginManager()


def init_app(app: Flask):

    login_manager.init_app(app)
    login_manager.login_view = "login_page"

    # --- Authentication Routes ---

    @app.route("/login", methods=["GET", "POST"])
    def login_page():
        form = LoginForm()
        if form.validate_on_submit():
            attempted_user = User.query.filter_by(email=form.email.data).first()
            if attempted_user and attempted_user.check_password(
                password=form.password.data
            ):
                login_user(attempted_user)
                flash(
                    f"You are logged in as: {attempted_user.name or attempted_user.email}",
                    category="success",
                )
                return redirect(url_for("admin_dashboard"))
            else:
                flash("Email or password incorrect", category="danger")
        return render_template("login.html", form=form)

    @app.route("/logout")
    @login_required
    def logout_page():
        logout_user()
        flash("You are now Logged Out, See you soon!", category="info")
        return redirect(url_for("login_page"))

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        flash("You must be logged in to view this page.", "warning")
        return redirect(url_for("login_page"))

    # --- Survey API Endpoints ---

    @app.route("/api/survey/token", methods=["POST"])
    def generate_token():
        try:
            new_token = ValidToken()
            db.session.add(new_token)
            db.session.commit()
            return jsonify({"success": True, "token": new_token.token}), 201
        except Exception as e:
            db.session.rollback()
            print(f"Error generating token: {e}")
            return jsonify({"success": False, "error": "Could not generate token"}), 500

    # GET to validate an existing token
    @app.route("/api/survey/token/<string:token_uuid>", methods=["GET"])
    def validate_token(token_uuid):
        """
        Checks if a given token UUID exists and is not used.
        """
        valid_token = ValidToken.query.filter_by(token=token_uuid).first()

        if not valid_token:
            # Token does not exist
            return jsonify({"valid": False, "reason": "not_found"}), 404

        if valid_token.used:
            # Token exists but has already been used
            return jsonify({"valid": False, "reason": "used"}), 409

        # Token exists and is not used
        return jsonify({"valid": True}), 200

    @app.route("/api/survey/submit", methods=["POST"])
    def submit_survey():
        data = request.get_json()
        if not data:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Invalid request format. JSON expected.",
                    }
                ),
                400,
            )

        token_str = data.get("token")
        survey_data = data.get("surveyData")

        if not token_str or not survey_data:
            return (
                jsonify({"success": False, "error": "Missing token or survey data"}),
                400,
            )

        valid_token = ValidToken.query.filter_by(token=token_str).first()

        if not valid_token:
            return jsonify({"success": False, "error": "Invalid token"}), 400

        if valid_token.used:
            return jsonify({"success": False, "error": "Token already used"}), 409

        try:
            new_response = SurveyResponse(
                genero=survey_data.get("genero"),
                localidad=survey_data.get("localidad"),
                edad=survey_data.get("edad"),
                intendente=survey_data.get("intendente"),
                balotaje=survey_data.get("balotaje"),
                estado=survey_data.get("estado"),
                partido_vs_persona=survey_data.get("partido_vs_persona"),
                percepcion_mario=survey_data.get("percepcion_mario"),
                percepcion_daniel=survey_data.get("percepcion_daniel"),
                problemas=survey_data.get("problemas"),
                auditoria=survey_data.get("auditoria"),
                telefono=survey_data.get("telefono"),
                device_type=survey_data.get("device_type"),
                ip_address=request.remote_addr,
                token_id=valid_token.id,
            )

            valid_token.used = True

            db.session.add(new_response)
            db.session.add(valid_token)
            db.session.commit()

            return (
                jsonify({"success": True, "message": "Survey submitted successfully"}),
                201,
            )

        except Exception as e:
            db.session.rollback()
            print(f"Error submitting survey: {e}")
            return jsonify({"success": False, "error": "Could not submit survey"}), 500

    # --- Admin Routes ---

    @app.route("/admin/dashboard")
    @login_required
    def admin_dashboard():
        # Obtener estadísticas básicas para mostrar en el dashboard
        total_responses = SurveyResponse.query.count()
        recent_responses = (
            SurveyResponse.query.order_by(SurveyResponse.submission_timestamp.desc())
            .limit(10)
            .all()
        )

        # Calcular cuántas encuestas se completaron hoy
        today = datetime.now().date()
        responses_today = SurveyResponse.query.filter(
            func.date(SurveyResponse.submission_timestamp) == today
        ).count()

        # Calcular tokens disponibles vs usados
        total_tokens = ValidToken.query.count()
        used_tokens = ValidToken.query.filter_by(used=True).count()
        available_tokens = total_tokens - used_tokens

        return render_template(
            "admin_dashboard.html",
            responses=recent_responses,
            total_responses=total_responses,
            responses_today=responses_today,
            available_tokens=available_tokens,
            used_tokens=used_tokens,
            total_tokens=total_tokens,
        )

    @app.route("/admin/stats")
    @login_required
    def admin_stats():
        # Estadísticas por género
        gender_stats = (
            db.session.query(
                SurveyResponse.genero, func.count(SurveyResponse.id).label("count")
            )
            .group_by(SurveyResponse.genero)
            .all()
        )

        gender_data = {
            "labels": [g[0] or "No especificado" for g in gender_stats],
            "data": [g[1] for g in gender_stats],
        }

        # Estadísticas por edad
        age_stats = (
            db.session.query(
                SurveyResponse.edad, func.count(SurveyResponse.id).label("count")
            )
            .group_by(SurveyResponse.edad)
            .all()
        )

        age_data = {
            "labels": [a[0] or "No especificado" for a in age_stats],
            "data": [a[1] for a in age_stats],
        }

        # Intención de voto (intendente)
        vote_stats = (
            db.session.query(
                SurveyResponse.intendente, func.count(SurveyResponse.id).label("count")
            )
            .group_by(SurveyResponse.intendente)
            .all()
        )

        vote_data = {
            "labels": [v[0] or "No especificado" for v in vote_stats],
            "data": [v[1] for v in vote_stats],
        }

        # Percepción de candidatos
        mario_stats = (
            db.session.query(
                SurveyResponse.percepcion_mario,
                func.count(SurveyResponse.id).label("count"),
            )
            .group_by(SurveyResponse.percepcion_mario)
            .all()
        )

        daniel_stats = (
            db.session.query(
                SurveyResponse.percepcion_daniel,
                func.count(SurveyResponse.id).label("count"),
            )
            .group_by(SurveyResponse.percepcion_daniel)
            .all()
        )

        candidates_data = {
            "mario": {
                "labels": [m[0] or "No especificado" for m in mario_stats],
                "data": [m[1] for m in mario_stats],
            },
            "daniel": {
                "labels": [d[0] or "No especificado" for d in daniel_stats],
                "data": [d[1] for d in daniel_stats],
            },
        }

        return render_template(
            "admin_stats.html",
            gender_data=gender_data,
            age_data=age_data,
            vote_data=vote_data,
            candidates_data=candidates_data,
        )

    @app.route("/admin/responses", methods=["GET", "POST"])
    @login_required
    def admin_responses():
        # Filtros
        filters = {}
        if request.method == "POST":
            if request.form.get("genero"):
                filters["genero"] = request.form.get("genero")
            if request.form.get("edad"):
                filters["edad"] = request.form.get("edad")
            if request.form.get("localidad"):
                filters["localidad"] = request.form.get("localidad")
            if request.form.get("intendente"):
                filters["intendente"] = request.form.get("intendente")

        # Consulta base
        query = SurveyResponse.query

        # Aplicar filtros
        for key, value in filters.items():
            query = query.filter(getattr(SurveyResponse, key) == value)

        # Opciones para filtros
        genero_options = db.session.query(SurveyResponse.genero).distinct().all()
        edad_options = db.session.query(SurveyResponse.edad).distinct().all()
        localidad_options = db.session.query(SurveyResponse.localidad).distinct().all()
        intendente_options = (
            db.session.query(SurveyResponse.intendente).distinct().all()
        )

        # Obtener respuestas filtradas
        responses = query.order_by(SurveyResponse.submission_timestamp.desc()).all()

        return render_template(
            "admin_responses.html",
            responses=responses,
            filters=filters,
            genero_options=genero_options,
            edad_options=edad_options,
            localidad_options=localidad_options,
            intendente_options=intendente_options,
        )

    @app.route("/admin/export", methods=["POST"])
    @login_required
    def export_responses():
        format_type = request.form.get("export_format", "csv")

        # Obtener todas las respuestas
        responses = SurveyResponse.query.order_by(
            SurveyResponse.submission_timestamp.desc()
        ).all()

        if format_type == "csv":
            # Crear un objeto de memoria para el CSV
            output = StringIO()
            writer = csv.writer(output)

            # Escribir encabezados
            headers = [
                "ID",
                "Fecha",
                "Género",
                "Edad",
                "Localidad",
                "Intendente",
                "Balotaje",
                "Estado",
                "Partido vs Persona",
                "Percepción Mario",
                "Percepción Daniel",
                "Problemas",
                "Auditoría",
                "Teléfono",
                "IP",
            ]
            writer.writerow(headers)

            # Escribir filas
            for resp in responses:
                writer.writerow(
                    [
                        resp.id,
                        resp.submission_timestamp,
                        resp.genero,
                        resp.edad,
                        resp.localidad,
                        resp.intendente,
                        resp.balotaje,
                        resp.estado,
                        resp.partido_vs_persona,
                        resp.percepcion_mario,
                        resp.percepcion_daniel,
                        resp.problemas,
                        resp.auditoria,
                        resp.telefono,
                        resp.ip_address,
                    ]
                )

            # Crear y enviar el archivo
            output.seek(0)
            return send_file(
                BytesIO(output.getvalue().encode("utf-8")),
                mimetype="text/csv",
                as_attachment=True,
                download_name=f'encuestas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            )

        elif format_type == "json":
            # Convertir a JSON
            data = []
            for resp in responses:
                data.append(
                    {
                        "id": resp.id,
                        "fecha": resp.submission_timestamp.isoformat(),
                        "genero": resp.genero,
                        "edad": resp.edad,
                        "localidad": resp.localidad,
                        "intendente": resp.intendente,
                        "balotaje": resp.balotaje,
                        "estado": resp.estado,
                        "partido_vs_persona": resp.partido_vs_persona,
                        "percepcion_mario": resp.percepcion_mario,
                        "percepcion_daniel": resp.percepcion_daniel,
                        "problemas": resp.problemas,
                        "auditoria": resp.auditoria,
                        "telefono": resp.telefono,
                        "ip": resp.ip_address,
                    }
                )

            # Crear y enviar el archivo
            return send_file(
                BytesIO(json.dumps(data, ensure_ascii=False).encode("utf-8")),
                mimetype="application/json",
                as_attachment=True,
                download_name=f'encuestas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            )

        # Si el formato no es válido
        flash("Formato de exportación no válido", "danger")
        return redirect(url_for("admin_responses"))

    @app.route("/admin/tokens", methods=["GET", "POST"])
    @login_required
    def admin_tokens():
        if request.method == "POST":
            action = request.form.get("action")

            if action == "generate":
                # Generar nuevos tokens
                num_tokens = int(request.form.get("num_tokens", 1))
                for _ in range(num_tokens):
                    new_token = ValidToken()
                    db.session.add(new_token)
                db.session.commit()
                flash(f"Se generaron {num_tokens} nuevos tokens", "success")

            # Otras acciones como invalidar tokens se pueden agregar aquí

        # Obtener todos los tokens
        tokens = ValidToken.query.order_by(ValidToken.created_at.desc()).all()

        return render_template("admin_tokens.html", tokens=tokens)

    # --- Error Handlers ---

    @app.errorhandler(404)
    def not_found(e):
        if (
            request.accept_mimetypes.accept_json
            and not request.accept_mimetypes.accept_html
        ):
            return jsonify({"success": False, "error": "Not Found"}), 404

        try:
            return render_template("notfound.html"), 404
        except TemplateNotFound:
            return (
                "<h1>404 - Not Found</h1><p>The requested URL was not found on the server.</p>",
                404,
            )

    @app.route("/")
    def index_redirect():
        return redirect(url_for("login_page"))
