from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import os

def generate_project_report():
    # Create the PDF file
    doc = SimpleDocTemplate(
        "School_Management_System_Report.pdf",
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Container for the 'Flowable' objects
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    elements.append(Paragraph("School Management System", title_style))
    elements.append(Paragraph("Project Report", title_style))
    
    # Date
    date_style = ParagraphStyle(
        'Date',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.gray
    )
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style))
    elements.append(Spacer(1, 20))

    # Project Overview
    elements.append(Paragraph("Project Overview", styles['Heading2']))
    overview_text = """
    The School Management System is a comprehensive web application designed to streamline the management of student records, 
    course information, and fee tracking in an educational institution. Built using Flask and SQLite, the system provides 
    a user-friendly interface for administrators to manage student data efficiently.
    """
    elements.append(Paragraph(overview_text, styles['Normal']))
    elements.append(Spacer(1, 20))

    # Features
    elements.append(Paragraph("Key Features", styles['Heading2']))
    features = [
        "Admin Authentication and Security",
        "Student Registration and Management",
        "Course Management",
        "Fee Tracking and Management",
        "Student Search Functionality",
        "Discount Management System",
        "Course-wise Student Grouping"
    ]
    
    for feature in features:
        elements.append(Paragraph(f"• {feature}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Technical Stack
    elements.append(Paragraph("Technical Stack", styles['Heading2']))
    tech_stack = [
        ["Backend Framework", "Flask"],
        ["Database", "SQLite"],
        ["Frontend", "HTML, CSS, Bootstrap"],
        ["Authentication", "Flask-Login"],
        ["ORM", "SQLAlchemy"],
        ["Template Engine", "Jinja2"]
    ]
    
    tech_table = Table(tech_stack, colWidths=[2*inch, 4*inch])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(tech_table)
    elements.append(Spacer(1, 20))

    # Database Schema
    elements.append(Paragraph("Database Schema", styles['Heading2']))
    schema_text = """
    The application uses three main database models:
    
    1. Admin: Manages administrator authentication
    2. Course: Stores course information including name, duration, and fees
    3. Student: Contains comprehensive student information including personal details and fee records
    """
    elements.append(Paragraph(schema_text, styles['Normal']))
    elements.append(Spacer(1, 20))

    # Course Information
    elements.append(Paragraph("Available Courses", styles['Heading2']))
    courses = [
        ["Course Name", "Duration", "Total Fees"],
        ["Bachelor of Technology", "4 years", "₹400,000"],
        ["Bachelor of Science", "3 years", "₹300,000"],
        ["Master of Technology", "2 years", "₹200,000"],
        ["Master of Science", "2 years", "₹180,000"],
        ["Bachelor of Commerce", "3 years", "₹250,000"],
        ["Bachelor of Arts", "3 years", "₹200,000"],
        ["Master of Business Administration", "2 years", "₹350,000"],
        ["Bachelor of Computer Applications", "3 years", "₹280,000"]
    ]
    
    course_table = Table(courses, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    course_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(course_table)
    elements.append(Spacer(1, 20))

    # Security Features
    elements.append(Paragraph("Security Features", styles['Heading2']))
    security_features = [
        "Password hashing using Werkzeug's security functions",
        "Session management with Flask-Login",
        "Protected routes requiring authentication",
        "Secure form handling and data validation"
    ]
    
    for feature in security_features:
        elements.append(Paragraph(f"• {feature}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Future Enhancements
    elements.append(Paragraph("Future Enhancements", styles['Heading2']))
    enhancements = [
        "Student attendance tracking system",
        "Online fee payment integration",
        "Parent portal access",
        "Student performance tracking",
        "Automated report generation",
        "Email notifications system"
    ]
    
    for enhancement in enhancements:
        elements.append(Paragraph(f"• {enhancement}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Build the PDF
    doc.build(elements)
    print("Project report generated successfully!")
    
if __name__ == "__main__":
    generate_project_report()
