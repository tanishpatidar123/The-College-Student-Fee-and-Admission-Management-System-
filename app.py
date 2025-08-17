from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import func
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Custom filter to format numbers with commas
@app.template_filter('format_number')
def format_number(value):
    try:
        return "{:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return value

# Database Models
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(50), nullable=False)  
    total_fees = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    students = db.relationship('Student', backref='course', lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enrollment_number = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    father_name = db.Column(db.String(100), nullable=False)
    mother_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    admission_date = db.Column(db.Date, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    total_fees = db.Column(db.Float, nullable=False)
    paid_fees = db.Column(db.Float, default=0.0)
    remaining_fees = db.Column(db.Float, nullable=False)



@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

def generate_enrollment_number():
    year = datetime.datetime.now().year
    last_student = Student.query.order_by(Student.id.desc()).first()
    if last_student:
        last_number = int(last_student.enrollment_number[-4:])
        new_number = last_number + 1
    else:
        new_number = 1
    return f"ENR{year}{new_number:04d}"

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Calculate dashboard statistics
    total_students = Student.query.count()
    total_courses = Course.query.count()
    
    # Calculate total fees collected and pending
    total_fees_collected = db.session.query(func.sum(Student.paid_fees)).scalar() or 0
    total_fees_pending = db.session.query(func.sum(Student.remaining_fees)).scalar() or 0

    return render_template('dashboard.html',
                         total_students=total_students,
                         total_courses=total_courses,
                         total_fees_collected=total_fees_collected,
                         total_fees_pending=total_fees_pending)

@app.route('/view_course_students/<int:course_id>')
@login_required
def view_course_students(course_id):
    course = Course.query.get_or_404(course_id)
    students = Student.query.filter_by(course_id=course_id).all()
    return render_template('course_students.html', course=course, students=students)

@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        try:
            course_id = request.form.get('course_id')
            enrollment_number = request.form.get('enrollment_number')
            
            if not course_id:
                flash('Please select a course', 'danger')
                return redirect(url_for('add_student'))

            if not enrollment_number:
                flash('Please enter enrollment number', 'danger')
                return redirect(url_for('add_student'))

            # Check if enrollment number already exists
            existing_student = Student.query.filter_by(enrollment_number=enrollment_number).first()
            if existing_student:
                flash('Enrollment number already exists! Please use a different number.', 'danger')
                return redirect(url_for('add_student'))

            course = Course.query.get(course_id)
            if not course:
                flash('Invalid course selected', 'danger')
                return redirect(url_for('add_student'))

            # Calculate fees with discount
            discount = float(request.form.get('discount', 0))
            total_fees = course.total_fees * (1 - discount / 100)

            student = Student(
                enrollment_number=enrollment_number,
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                date_of_birth=datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date(),
                gender=request.form['gender'],
                father_name=request.form['father_name'],
                mother_name=request.form['mother_name'],
                address=request.form['address'],
                phone=request.form['phone'],
                email=request.form['email'],
                admission_date=datetime.now().date(),
                course_id=course_id,
                total_fees=total_fees,
                remaining_fees=total_fees
            )
            db.session.add(student)
            db.session.commit()
            flash(f'Student added successfully! Enrollment Number: {enrollment_number}', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            print("Error:", str(e))
            flash(f'Error adding student: {str(e)}', 'danger')
            db.session.rollback()
            return redirect(url_for('add_student'))
    
    courses = Course.query.all()
    return render_template('add_student.html', courses=courses)

@app.route('/search_student', methods=['GET', 'POST'])
@login_required
def search_student():
    enrollment_number = request.args.get('enrollment_number') or request.form.get('enrollment_number')
    name = request.args.get('name') or request.form.get('name')
    
    if enrollment_number:
        student = Student.query.filter_by(enrollment_number=enrollment_number).first()
        if student:
            return render_template('student_details.html', student=student)
        flash('Student not found!')
    elif name:
        # Search by name (first name or last name)
        students = Student.query.filter(
            (Student.first_name.ilike(f'%{name}%')) | 
            (Student.last_name.ilike(f'%{name}%'))
        ).all()
        
        if students:
            if len(students) == 1:
                # If only one student found, show details directly
                return render_template('student_details.html', student=students[0])
            else:
                # If multiple students found, show list
                return render_template('search_results.html', students=students, search_term=name)
        else:
            flash('No students found with that name!')
    elif request.method == 'POST':
        flash('Please enter an enrollment number or name')
    
    return render_template('search_student.html')

@app.route('/view_students')
@login_required
def view_students():
    # Get all courses with their students
    courses = Course.query.all()
    print(f"Found {len(courses)} courses")
    for course in courses:
        print(f"Course: {course.name}, Students: {len(course.students)}")
    return render_template('view_students.html', courses=courses)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/get_course_fees/<int:course_id>')
@login_required
def get_course_fees(course_id):
    course = Course.query.get_or_404(course_id)
    return jsonify({
        'total_fees': course.total_fees,
        'duration': course.duration
    })

@app.route('/add_admin', methods=['GET', 'POST'])
@login_required
def add_admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not password:
            flash('Please fill in all fields', 'danger')
            return redirect(url_for('add_admin'))

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('add_admin'))

        if Admin.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('add_admin'))

        admin = Admin(
            username=username,
            password_hash=generate_password_hash(password)
        )
        db.session.add(admin)
        db.session.commit()
        flash('Admin added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_admin.html')

@app.route('/generate_report')
@login_required
def generate_report():
    try:
        from generate_report import generate_project_report
        generate_project_report()
        flash('Report generated successfully!', 'success')
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/pay_fees/<int:student_id>', methods=['GET', 'POST'])
@login_required
def pay_fees(student_id):
    student = Student.query.get_or_404(student_id)
    
    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount', 0))
            
            if amount <= 0:
                flash('Please enter a valid amount greater than 0', 'danger')
                return redirect(url_for('pay_fees', student_id=student.id))
                
            if amount > student.remaining_fees:
                flash(f'Amount exceeds remaining fees (₹{student.remaining_fees:.2f})', 'danger')
                return redirect(url_for('pay_fees', student_id=student.id))
            
            # Update student fees
            student.paid_fees += amount
            student.remaining_fees -= amount
            
            db.session.commit()
            flash(f'Payment of ₹{amount:.2f} recorded successfully!', 'success')
            return redirect(url_for('student_details', student_id=student.id))
            
        except ValueError:
            flash('Please enter a valid amount', 'danger')
            return redirect(url_for('pay_fees', student_id=student.id))
    
    return render_template('pay_fees.html', student=student)

@app.route('/student_details/<int:student_id>')
@login_required
def student_details(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template('student_details.html', student=student)

@app.route('/fee_dashboard')
@login_required
def fee_dashboard():
    # Get students with pending fees, ordered by highest remaining amount
    students_with_pending_fees = Student.query.filter(Student.remaining_fees > 0).order_by(Student.remaining_fees.desc()).all()
    
    # Get recent fee payments (could be implemented with a Payment model in a real system)
    # For now, we'll pass the list of students with pending fees
    
    return render_template('fee_dashboard.html', 
                          students=students_with_pending_fees,
                          total_pending=db.session.query(func.sum(Student.remaining_fees)).scalar() or 0)

@app.route('/update_student/<int:student_id>', methods=['GET', 'POST'])
@login_required
def update_student(student_id):
    student = Student.query.get_or_404(student_id)
    
    if request.method == 'POST':
        try:
            # Update student information
            student.first_name = request.form['first_name']
            student.last_name = request.form['last_name']
            student.date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
            student.gender = request.form['gender']
            student.father_name = request.form['father_name']
            student.mother_name = request.form['mother_name']
            student.address = request.form['address']
            student.phone = request.form['phone']
            student.email = request.form['email']
            
            # Update course if changed
            if request.form.get('course_id'):
                course_id = int(request.form['course_id'])
                if course_id != student.course_id:
                    course = Course.query.get(course_id)
                    if course:
                        student.course_id = course_id
                        student.total_fees = course.total_fees
                        student.remaining_fees = student.total_fees - student.paid_fees
            
            db.session.commit()
            flash('Student information updated successfully!', 'success')
            return redirect(url_for('student_details', student_id=student.id))
            
        except Exception as e:
            flash(f'Error updating student: {str(e)}', 'danger')
            db.session.rollback()
    
    courses = Course.query.all()
    return render_template('update_student.html', student=student, courses=courses)

@app.route('/delete_student/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    try:
        student = Student.query.get_or_404(student_id)
        db.session.delete(student)
        db.session.commit()
        flash('Student deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting student: {str(e)}', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/student_report/<int:student_id>')
@login_required
def student_report(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template('student_report.html', student=student)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create sample admin if none exists
        if not Admin.query.first():
            admin = Admin(
                username='admin',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            print("Sample admin created successfully!")
        
        # Create sample courses if none exist
        if not Course.query.first():
            courses = [
                Course(name='B.Tech Computer Science', duration='4 years', total_fees=90000),
                Course(name='B.Tech Artificial Intelligence & Data Science', duration='4 years', total_fees=65000),
                Course(name='B.Tech Information Technology', duration='4 years', total_fees=45000),
                Course(name='B.Tech Electronics', duration='4 years', total_fees=40000),
                Course(name='B.Tech Mechanical', duration='4 years', total_fees=35000),
                Course(name='B.Tech Civil', duration='4 years', total_fees=30000),
                Course(name='M.Tech Computer Science', duration='2 years', total_fees=60000),
                Course(name='M.Tech Information Technology', duration='2 years', total_fees=55000),
                Course(name='M.Tech Electronics', duration='2 years', total_fees=50000),
                Course(name='M.Tech Mechanical', duration='2 years', total_fees=45000),
                Course(name='M.Tech Civil', duration='2 years', total_fees=40000)
            ]
            for course in courses:
                db.session.add(course)
            db.session.commit()
            print("Sample courses created successfully!")
        
        # Create sample students if none exist
        if not Student.query.first():
            import random
            from datetime import datetime, timedelta
            
            # List of first names and last names for random generation
            first_names = ['Aarav', 'Aditya', 'Aisha', 'Akash', 'Amit', 'Ananya', 'Anjali', 'Arjun', 'Arun', 'Ashish',
                          'Bhavya', 'Chandra', 'Deepak', 'Divya', 'Esha', 'Gaurav', 'Geeta', 'Harsh', 'Indira', 'Jatin',
                          'Kavita', 'Lakshmi', 'Madhav', 'Neha', 'Om', 'Pooja', 'Rahul', 'Ravi', 'Sanjay', 'Tara',
                          'Uma', 'Vikram', 'Yash', 'Zara', 'Aryan', 'Bharat', 'Chitra', 'Dinesh', 'Elena', 'Firoz',
                          'Gita', 'Hari', 'Isha', 'Jaya', 'Krishna', 'Lata', 'Mohan', 'Nisha', 'Omar', 'Priya']
            
            last_names = ['Sharma', 'Verma', 'Patel', 'Singh', 'Kumar', 'Gupta', 'Chauhan', 'Reddy', 'Pandey', 'Mishra',
                         'Agarwal', 'Malhotra', 'Joshi', 'Iyer', 'Menon', 'Nair', 'Pillai', 'Rao', 'Sastry', 'Tiwari',
                         'Varma', 'Yadav', 'Zachariah', 'Acharya', 'Bhat', 'Chakraborty', 'Das', 'Eswar', 'Fernandes',
                         'Ganguly', 'Hegde', 'Iyengar', 'Jain', 'Krishna', 'Lal', 'Mehta', 'Nambiar', 'Ojha', 'Prakash',
                         'Rajan', 'Saxena', 'Tandon', 'Uppal', 'Vaidya', 'Wadhwa', 'Xavier', 'Yadav', 'Zachariah']
            
            # Create 100 students
            for i in range(100):
                # Generate unique enrollment number
                enrollment_no = generate_enrollment_number()
                
                # Generate random name
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                
                # Generate random date of birth (18-25 years old)
                days = random.randint(18*365, 25*365)
                dob = datetime.now() - timedelta(days=days)
                
                # Generate random gender
                gender = random.choice(['Male', 'Female'])
                
                # Generate random email
                email = f"{first_name.lower()}{random.randint(100, 999)}@example.com"
                
                # Generate random phone number
                phone = f"+91{random.randint(6000000000, 9999999999)}"
                
                # Select random course
                course = random.choice(Course.query.all())
                
                # Generate random fees with some students having discounts
                total_fees = int(course.total_fees)  # Convert to integer
                if random.random() < 0.3:  # 30% chance of discount
                    discount = random.randint(5, 25)  # 5-25% discount
                    total_fees = int(total_fees * (1 - discount/100))
                
                # Generate random paid and remaining fees
                paid_fees = random.randint(0, total_fees)
                remaining_fees = total_fees - paid_fees
                
                # Create student
                student = Student(
                    enrollment_number=enrollment_no,
                    first_name=first_name,
                    last_name=last_name,
                    date_of_birth=dob,
                    gender=gender,
                    father_name=f"Father of {first_name}",
                    mother_name=f"Mother of {first_name}",
                    address=f"Address {random.randint(1, 100)}",
                    phone=phone,
                    email=email,
                    admission_date=datetime.now().date(),
                    course_id=course.id,
                    total_fees=float(total_fees),  # Convert back to float for database
                    paid_fees=float(paid_fees),     # Convert back to float for database
                    remaining_fees=float(remaining_fees)  # Convert back to float for database
                )
                db.session.add(student)
            
            db.session.commit()
            print("100 sample students created successfully!")
    
    app.run(debug=True) 