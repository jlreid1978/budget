from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
import user
import budget
from insta import extract_zip, parse_followers, parse_following
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
admin_users = ['jreid']

# Setup logging
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'budget.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Instagram project configurations
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/upload', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        zip_file = request.files['zip_file']

        if not zip_file:
            flash("No file part", 'error')
            return redirect(url_for('upload_files'))

        zip_path = os.path.join(app.config['UPLOAD_FOLDER'], zip_file.filename)
        zip_file.save(zip_path)

        extract_to = os.path.join(app.config['UPLOAD_FOLDER'], 'extracted')
        os.makedirs(extract_to, exist_ok=True)
        extract_zip(zip_path, extract_to)

        followers = parse_followers(extract_to)
        following = parse_following(extract_to)
        if following is None:
            flash("following.json not found in the zip file", 'error')
            return redirect(url_for('upload_files'))

        not_following_back = [user for user in following if user not in followers]

        return render_template('results.html', not_following_back=not_following_back)

    return render_template('insta.html')

# Main route for the title page
@app.route('/')
def title_page():
    return render_template('title.html')

# Existing routes for the Budget project
@app.route('/budget-home', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'reset_username' in request.form:
            if 'username' in session and session['username'] in admin_users:
                reset_username = request.form['reset_username']
                try:
                    user.reset_password(reset_username)
                    flash(f"Password for {reset_username} reset successfully to default.", 'success')
                except ValueError as e:
                    flash(str(e), 'error')
                except Exception as e:
                    flash("Failed to reset password", 'error')
            else:
                flash("Unauthorized action", 'error')
            return redirect(url_for('index'))

    is_admin = 'username' in session and session['username'] in admin_users
    return render_template('index.html', is_admin=is_admin)

# Route for admin to reset passwords
@app.route('/reset-password', methods=['POST'])
def reset_password():
    if 'reset_username' in request.form:
        if 'username' in session and session['username'] in admin_users:
            reset_username = request.form['reset_username']
            try:
                user.reset_password(reset_username)
                flash(f"Password for {reset_username} reset successfully to default.", 'success')
            except ValueError as e:
                flash(str(e), 'error')
            except Exception as e:
                flash("Failed to reset password", 'error')
        else:
            flash("Unauthorized action", 'error')

    return redirect(url_for('index'))

# Logout route
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)  
    return redirect(url_for('login'))

# Route to register a new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash("Passwords do not match", 'error')
            return render_template('register.html')
        try:
            message = user.register_user(name, username, password)
            flash(message)
        except Exception as e:
            print(f'an error has occurred registering user: {e}')
            return render_template('error.html', error_message="Failed to register user")
        if message == "Registration successful":
            return redirect('/budget-home') 
            
    return render_template('register.html')

# Route to inject username and name into html
@app.context_processor
def inject_logged_in():
    logged_in = 'username' in session
    username = session.get('username', None)
    name = session.get('name', None)
    return {'logged_in': logged_in, 'username': username, 'name': name}

# Route to login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            if user.verify_login(username, password):
                session['username'] = username  
                session['name'] = user.get_name(username) 
                flash(f'Welcome {username}', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password', 'error')
        except Exception as e:
            print(f'an error has occurred logging in user: {e}')
            return render_template('error.html', error_message="Failed to log in user")        
    return render_template('login.html')

# Route to delete user from the database
@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        username = session.get('username')
        if username:
            user.delete_user(username)
            session.clear()
            flash("Account deleted successfully", 'success')
            return redirect(url_for('login'))
        else:
            flash('There has been an error deleting the account.', 'error')
    else:
        return render_template('delete.html')

# Route to change password
@app.route('/change-password', methods=['GET', 'POST'])
def change_password_route():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        username = session['username']

        if new_password != confirm_password:
            flash('New password and confirm password do not match', 'error')
            return redirect(url_for('change_password_route'))
        try:
            user.change_password(username, current_password, new_password)
            flash('Password changed successfully', 'success')
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash("Failed to update password", 'error')
        return redirect(url_for('change_password_route'))

    return render_template('change_password.html')

# Route to build the budget
@app.route('/budget', methods=['GET', 'POST'])
def build_budget():
    if request.method == 'POST':
        try:
            user_id = user.get_user_id(session.get('username'))
            description = request.form['description']
            amount = float(request.form['amount'])
            type = request.form['type']
            frequency = request.form['frequency']
            date = request.form['date']
            budget.add_budget(user_id, description, amount, type, frequency, date)
            flash('Budget item added successfully!', 'success')
            return redirect(url_for('build_budget'))
        except Exception:
            return render_template('error.html', error_message="Failed to send to database")
    return render_template('build.html')

# Route to view the user's budget
@app.route('/view', methods=['GET'])
def view_budget():
    user_id = user.get_user_id(session.get('username'))
    selected_month = request.args.get('month', None)
    
    try:
        budget_data = budget.get_user_budget(user_id)
    except Exception as e:
        print(f"An error occurred pulling budget data: {e}")
        return render_template('error.html', error_message="Failed to retrieve from database")
    
    # Generate a list of months for the dropdown
    today = date.today()
    months = generate_month_list(today)

    # Filter the budget data by selected month if provided
    if selected_month:
        budget_data = [entry for entry in budget_data if entry['date'].startswith(selected_month)]
    else:
        # If no month is selected, default to the current month
        selected_month = today.strftime("%Y-%m")
        budget_data = [entry for entry in budget_data if entry['date'].startswith(selected_month)]
    
    # Sort the budget data by date
    budget_data = sorted(budget_data, key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))

    # Calculate the total sum of amounts
    total_sum = sum(entry['amount'] for entry in budget_data)
    
    return render_template(
        'view.html', 
        budget_data=budget_data, 
        selected_month=selected_month, 
        months=months, 
        total_sum=total_sum
    )

# Helper function for viewing the budget
def generate_month_list(today):
    # Generate a list of months for the previous year, current year, and next year
    start_date = today.replace(year=today.year - 1, month=today.month, day=1)
    end_date = today.replace(year=today.year + 1, month=today.month, day=1)
    months = []
    current_date = start_date
    
    while current_date <= end_date:
        months.append(current_date.strftime('%Y-%m'))
        # Move to the next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return months

# Route to populate the page showing a user's budget entries
@app.route('/edit', methods=['GET'])
def edit_budget(): 
    try:
        # Fetch all budget entries for the logged-in user
        user_id = user.get_user_id(session.get('username'))
        budget_entries = budget.get_user_budget_entries(user_id)
        for i in budget_entries:
            print(i)
        return render_template('edit.html', budget_entries=budget_entries)
    except Exception as e:
        print(f"An error occurred saving edit: {e}")
        return render_template('error.html', error_message="Failed to retrieve from database")

# Route to edit budget entries
@app.route('/edit/<int:entry_id>', methods=['POST'])
def edit_budget_entry(entry_id):
    try:
        updated_description = request.form[f'description_{entry_id}']
        updated_amount = request.form[f'amount_{entry_id}']
        updated_frequency = request.form[f'frequency_{entry_id}']
        updated_date = request.form[f'date_{entry_id}']
    except Exception as e:
        print(f"An error occurred: {e}")
        return render_template('error.html', error_message="Error with form data")
    try:
        budget.update_budget_entry(entry_id, updated_description, updated_amount, updated_frequency, updated_date)
    except Exception as e:
        print(f"An error occurred saving edit: {e}")
        return render_template('error.html', error_message="Failed to update entry")
    flash('Budget entry updated successfully', 'success')
    return redirect(url_for('edit_budget'))

# Route to complete delete entry from user's budget
@app.route('/delete-entry/<int:entry_id>', methods=['GET'])
def delete_budget_entry(entry_id):
    try:
        budget.delete_budget_entry(entry_id)
        flash('Budget entry deleted successfully', 'success')
    except Exception as e:
        print(f"An error occurred deleting entry: {e}")
        return render_template('error.html', error_message="Failed to delete entry")
    return redirect(url_for('edit_budget'))


@app.route('/resume')
def resume():
    return render_template('resume.html')

if __name__ == "__main__":
    app.run(debug=True)
