from application import app, db
from flask_login import login_required, current_user
from flask import render_template, request, redirect, url_for

from application.kirjaus.models import Kirjaus
from application.kirjaus.forms import KirjausForm

from datetime import datetime, time, date
from sqlalchemy import desc

@app.route("/kirjaus", methods=["GET"])
@login_required
def kirjaus_index():
    return render_template("kirjaus/list.html", kirjauslista = Kirjaus.query.order_by(desc(Kirjaus.sisaankirjaus)).all())

@app.route("/kirjaus/new/")
@login_required
def kirjaus_form():
    return render_template("kirjaus/new.html", form = KirjausForm())

@app.route("/kirjaus/<kirjaus_id>/", methods=["POST"])
@login_required
def kirjaus_uloskirjaus(kirjaus_id):

    kirjaus = Kirjaus.query.get(kirjaus_id)
    now = datetime.now()
    kirjaus.uloskirjaus = datetime(now.year, now.month, now.day, now.hour, now.minute)
    db.session().commit()

    return redirect(url_for("kirjaus_index"))

@app.route("/kirjaus/delete/<kirjaus_id>", methods=["POST"])
@login_required
def kirjaus_poista(kirjaus_id):
    Kirjaus.query.filter_by(id = kirjaus_id).delete()
    db.session().commit()
    return redirect(url_for("kirjaus_index"))

@app.route("/kirjaus/sisaan", methods=["POST"])
@login_required
def kirjaus_sisaan():
    now = datetime.now()
    kirjaus_sisaan = Kirjaus(datetime(now.year, now.month, now.day, now.hour, now.minute))
    kirjaus_sisaan.account_id = current_user.id

    db.session().add(kirjaus_sisaan)
    db.session().commit()

    return redirect(url_for("kirjaus_index"))

@app.route("/kirjaus/", methods=["POST"])
@login_required
def kirjaus_create():
    form = KirjausForm(request.form)

    if not form.validate():
        return render_template("kirjaus/new.html", form = form)
    
    sisaan = datetime.combine(form.aika.data, form.time.data)
    ulos = datetime.combine(form.aika.data, form.timeout.data)

    minuutit = (int((ulos - sisaan).total_seconds())/60)
            
    kirjaus = Kirjaus(sisaan)
    kirjaus.uloskirjaus = ulos
    kirjaus.tehdytMinuutit = minuutit
    kirjaus.account_id = current_user.id

    db.session().add(kirjaus)
    db.session().commit()
    
    return redirect(url_for("kirjaus_index"))

