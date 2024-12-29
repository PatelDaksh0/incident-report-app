from flask import Flask, render_template, redirect, request, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import csv

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.sqlite3'
app.secret_key = 'NATIONALINCIDENTREPORTAPPBYMOKSHARTH@$'
db = SQLAlchemy(app)


class Users(db.Model):
  _id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(230), nullable=False, unique=True)
  password = db.Column(db.String(100), nullable=False)

  def __init__(self, email, password):
    self.email = email
    self.password = password


class Incidents(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  State = db.Column(db.String(2), nullable=False)
  Zip_Code = db.Column(db.Integer, nullable=False)
  Incident_Type = db.Column(db.String(130), nullable=False)
  Incident_Description = db.Column(db.String(1000), nullable=False)
  Location = db.Column(db.String(250), nullable=False)
  Date_Added = db.Column(db.Integer, default=datetime.today)

  def __init__(self, State, Zip_Code, Incident_Type, Incident_Description,
               Location):
    self.State = State
    self.Zip_Code = Zip_Code
    self.Incident_Type = Incident_Type
    self.Incident_Description = Incident_Description
    self.Location = Location


@app.route('/', methods=['POST', 'GET'])
def login():
  if 'user' in session:
    return redirect(url_for('incidents'))
  elif request.method == 'POST':
    if 'email' in request.form and 'password' in request.form:
      user = request.form['email']
      Email_Check = Users.query.filter_by(email=user).first()
      if Email_Check:
        user_id = Email_Check._id
        password = request.form['password']
        if password == Email_Check.password:
          session['user'] = user
          return redirect(url_for('incidents'))
        else:
          return render_template('login.html',
                                 error="Email Or Password is/are incorrect")
      else:
        return render_template('login.html',
                               error="Email Or Password is/are incorrect")
    else:
      return 'Bad Request: Email or password field is missing.'
  else:
    return render_template("login.html")


@app.route("/incident", methods=["GET", "POST"])
def incidents():
  if 'user' in session:
    if request.method == "GET":
      incidents_to_display = Incidents.query.order_by(
          Incidents.id.desc()).all()
      return render_template("incidents.html",
                             incidents_to_display=incidents_to_display)
    elif request.method == "POST":
      Zip_Searched = request.form['search']
      incidents_to_display = Incidents.query.filter_by(
          Zip_Code=Zip_Searched).order_by(Incidents.id.desc()).all()
      return render_template("incidents.html",
                             incidents_to_display=incidents_to_display)
  else:
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
  if 'user' in session:
    session.pop('user', None)
  return redirect(url_for('login'))


@app.route('/Create_Account', methods=['POST', 'GET'])
def signup():
  if request.method == 'POST':
    if 'signup' in request.form and 'sighuppass' in request.form and 'DOB' in request.form:
      signup_email = request.form['signup']
      signup_password = request.form['sighuppass']
      new_user = Users(email=signup_email, password=signup_password)
      db.session.add(new_user)
      try:
        db.session.commit()
        return render_template("sign up transfer.html")
      except:
        return render_template("sighup.html", error="User already exists")
    else:
      return 'Bad Request: Form data is missing or invalid.'
  else:
    return render_template("sighup.html")


@app.route('/Report', methods=['POST', 'GET'])
def report():
  if 'user' in session:
    if request.method == 'GET':
      return render_template('reportincidents.html')
    elif request.method == 'POST':
      if "state" in request.form and "Zip" in request.form and "Location" in request.form and "Type" in request.form and "Desc" in request.form:
        state_entered = request.form["state"]
        zip_entered = request.form["Zip"]
        type_enetered = request.form["Type"]
        desc_entered = request.form["Desc"]
        location_entered = request.form["Location"]
        new_incident = Incidents(State=state_entered,
                                 Zip_Code=zip_entered,
                                 Incident_Type=type_enetered,
                                 Incident_Description=desc_entered,
                                 Location=location_entered)
        db.session.add(new_incident)
        try:
          db.session.commit()
        except:
          redirect("/Report")
        return redirect("/incident")
      else:
        return "<h1>Fill out all the fields</h1>"
  else:
    return redirect(url_for("login"))


if __name__ == "__main__":
  with app.app_context():
    db.create_all()
  app.run(debug=False, host='0.0.0.0', port=5000)
