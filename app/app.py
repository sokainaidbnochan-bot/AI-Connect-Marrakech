from flask import Flask, render_template, request, redirect, url_for, session
from data_access import get_entreprises, get_repartition_categorie, get_repartition_quartier

app = Flask(__name__)
app.secret_key = "change-cette-cle-plus-tard"  # نécessaire pour utiliser session


@app.route('/')
def landing():
    return render_template('landing.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        session['username'] = username or 'Invité'
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('landing'))


@app.route('/dashboard')
def dashboard():
    entreprises = get_entreprises()
    return render_template(
        'dashboard.html',
        entreprises=entreprises[:5],
        total=len(entreprises),
        repartition_cat=get_repartition_categorie(),
        repartition_quartier=get_repartition_quartier(),
    )


@app.route('/entreprises')
def entreprises():
    return render_template('entreprises.html', entreprises=get_entreprises())


@app.route('/carte')
def carte():
    return render_template('carte.html', entreprises=get_entreprises())


@app.route('/suivi')
def suivi():
    return render_template('suivi.html')


if __name__ == '__main__':
    app.run(debug=True)