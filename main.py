import os
from flask import Flask, render_template, request
import smtplib
import requests
from datetime import datetime, timedelta
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from dotenv import load_dotenv

load_dotenv()


OWN_EMAIL = os.getenv('OWN_EMAIL')
OWN_PASSWORD = os.getenv('OWN_PASSWORD')

app = Flask(__name__, template_folder='templates', static_folder='static')
Bootstrap(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


class NewsForm(FlaskForm):
    news_name = StringField(u'Search keyword :', validators=[DataRequired()])
    submit = SubmitField(u'Submit')


@app.route('/', methods=['GET', 'POST'])
def get_all_posts(posts=None):
    form = NewsForm()
    if form.validate_on_submit():
        NEWS_ABOUT = form.news_name.data
        news_kw = NEWS_ABOUT.split(" ")
        required_date = datetime.now() - timedelta(days=5, hours=-5)
        from_date = f"{required_date.year}-{required_date.month}-{required_date.day}"

        parameters = {
            "q": news_kw[0],
            "from": from_date,
            "sortBy": "publishedAt",
            "apiKey": os.getenv('newsapi_apiKey')
        }

        response = requests.get("https://newsapi.org/v2/everything?", parameters)
        response.raise_for_status()
        data = response.json()
        posts = data['articles'][1:5]
    return render_template("index.html", form=form, all_posts=posts)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=['POST', 'GET'])
def contact():
    if request.method == 'POST':
        data = request.form
        send_email(data["name"], data["mail"], data["tel"], data["message"])
        return render_template("contact.html", msg_sent=True)
    return render_template("contact.html", msg_sent=False)


def send_email(name, mail, tel, message):
    email_message = f"Subject:New Message\n\nName: {name}\nEmail: {mail}\nPhone: {tel}\nMessage:{message}"
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(OWN_EMAIL, OWN_PASSWORD)
        connection.sendmail(OWN_EMAIL, OWN_EMAIL, email_message)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
#     app.run(debug=True)
