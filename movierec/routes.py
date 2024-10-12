from flask import render_template, url_for, flash, redirect, request
import requests 
from movierec import app, db, bcrypt
from movierec.forms import SignupForm, LoginForm 
from movierec.models import User
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        return render_template('dashboard.html')
    else:
        return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Signup', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home')) 
    form = LoginForm() 
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user) 
            flash('Login successful!', 'success')  
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check your email and password', 'danger')
    return render_template('login.html', form=form)

@app.route("/logout")
@login_required  # Protect the logout route
def logout():
    logout_user()
    flash('You have been logged out!', 'success')  # Flash a logout message
    return redirect(url_for('home'))

BASE_URL = 'http://www.omdbapi.com/'
API_KEY = '593db72e'

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    # Get search parameters from the request
    genre = request.args.get('genre', '')
    year = request.args.get('year', '')
    language = request.args.get('language', '')
    country = request.args.get('country', '')
    movie_name = request.args.get('movie_name', '')  # New parameter for movie name
    page = int(request.args.get('page', 1))  # Get the current page number from the request, default is 1

    recommendations = []
    total_movies = 0
    total_pages = 0
    has_next = False
    has_prev = False

    # Only perform the search if the user has provided at least one filter
    if genre or year or language or country or movie_name:  # Include movie_name in condition
        query_params = {
            'apikey': API_KEY,
            's': movie_name or genre or '',  # Use movie_name as the main search string
            'y': year or '',
            'language': language or '',
            'country': country or '',
            'page': page  # Include the page number in the API request
        }

        # Make the API request
        response = requests.get(BASE_URL, params=query_params)

        if response.status_code == 200:
            data = response.json()

            if data.get('Response') == 'True':
                movies = data.get('Search', [])
                total_movies = int(data.get('totalResults', 0))  # Get total results for pagination

                # Calculate total pages (OMDB returns 10 results per page)
                total_pages = (total_movies + 9) // 10  # Round up to the nearest whole page

                # Fetch detailed movie information for each found movie
                for movie in movies:
                    movie_id = movie['imdbID']
                    movie_details_response = requests.get(f"{BASE_URL}?apikey={API_KEY}&i={movie_id}")
                    movie_details = movie_details_response.json()

                    recommendations.append({
                        'title': movie_details.get('Title'),
                        'year': movie_details.get('Year'),
                        'genre': movie_details.get('Genre'),
                        'language': movie_details.get('Language'),
                        'country': movie_details.get('Country'),
                        'poster': movie_details.get('Poster', 'https://via.placeholder.com/300'),
                    })

                # Check if there are next or previous pages
                has_next = page < total_pages
                has_prev = page > 1
            else:
                flash('No movies found matching your criteria.', 'danger')
        else:
            flash('Could not fetch movie data from OMDB.', 'danger')

    return render_template('dashboard.html', recommendations=recommendations, has_next=has_next, has_prev=has_prev, page=page, total_pages=total_pages)
