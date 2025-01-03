from flask import Flask, render_template, redirect, request
from flask import current_app as app
from .models import *
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, not_

import matplotlib.pyplot as plt
import io, base64

from .config import login_manager
from flask_login import login_user, logout_user, login_required, current_user

import os
from werkzeug.utils import secure_filename

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))




@app.route('/')
def home():
    return render_template('index.html')


@app.route('/userlogin', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        this_user = Users.query.filter_by(username=username).first()
        if this_user and this_user.is_active == True and this_user.username == username:
            if this_user.password == password:
                login_user(this_user)
                return redirect(f'/userhome')
            else:
                return "INCORRECT PASSWORD"
        else:
            return "USER DOES NOT EXIST!"
    return render_template('2_user_login.html')


@app.route('/userlogout')
def userlogout():
    logout_user()
    return redirect('/userlogin')


@app.route('/adminlogin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        this_user = Users.query.filter_by(username=username).first()
        if this_user and this_user.username == username and this_user.user_type == 'admin':
            if this_user.password == password:
                login_user(this_user)
                return redirect(f'/adminhome')
            else:
                return "INCORRECT PASSWORD"
        else:
            return "USER DOES NOT EXIST!"
    return render_template('1_admin_login.html')


@app.route('/adminlogout')
def adminlogout():
    logout_user()
    return redirect('/adminlogin')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        this_user = Users.query.filter_by(username=username).first()
        if username and password:
            if password == confirm_password:
                if this_user:
                    return "USER ALREADY EXIST!"
                else:
                    new_user = Users(username=username, password=password)
                    db.session.add(new_user)
                    db.session.commit()
                    return "ACCOUNT CREATED SUCCESSFULLY"
            else:
                return "PASSWORD DOES NOT MATCH"
        else:
            return "PLEASE ENTER USERNAME AND PASSWORD"
    return render_template('0_register.html')

@app.route('/userhome', methods = ['GET', 'POST'] )
@login_required	
def user_home():
    user_id = current_user.id
    this_user = Users.query.get(user_id)
    books = Books.query.all()
    active_books = [book for book in books if book.is_active == True]

    issued_transactions = Transactions.query.filter_by(user_id=user_id).filter(Transactions.status == 'issued').all()
    issued_books = [trans.book for trans in issued_transactions]

    return render_template('2.0_user_home.html',this_user=this_user, active_books=active_books, issued_books=issued_books)



@app.route('/user', methods = ['GET', 'POST'] )
@login_required	
def user_dash():
    user_id = current_user.id
    this_user = Users.query.get(user_id)
    books = Books.query.all()
    sections = Sections.query.all()
    active_books = [book for book in books if book.is_active == True]

    issued_transactions = Transactions.query.filter_by(user_id=user_id).filter(Transactions.status == 'issued').all()
    issued_books = [trans.book for trans in issued_transactions]

    return render_template('2.1_user_dash.html',this_user=this_user, sections=sections, active_books=active_books, issued_books=issued_books)


@app.route('/adminhome', methods = ['GET', 'POST'] )
@login_required	
def admin_home():
    if current_user.user_type == 'admin':
        admin_id = current_user.id
        admin = Users.query.get(admin_id)
        active_books = Books.query.filter_by(is_active = True).all()
        return render_template('1.0_admin_home.html', admin=admin, active_books=active_books)
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"




@app.route('/admindash', methods = ['GET', 'POST'] )
@login_required	
def admin_dash():
    if current_user.user_type == 'admin':
        admin_id = current_user.id
        admin = Users.query.get(admin_id)
        sections = Sections.query.all()
        active_books = Books.query.filter_by(is_active = True).all()
        return render_template('1.1_admin_dash.html', admin=admin, sections=sections, active_books=active_books)
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"


@app.route('/addsection', methods=['GET', 'POST'])
@login_required	
def add_section():
    if current_user.user_type == 'admin':
        admin_id = current_user.id
        admin = Users.query.get(admin_id)
        if request.method == 'POST':
            section_name = request.form.get('section_name')
            description = request.form.get('description')
            if section_name and description:
                section_query = Sections.query.filter_by(name=section_name).first()
                create_time = datetime.now()
                if not section_query:
                    search = search_string_convert(section_name)
                    new_section = Sections(name=section_name, description=description, date_created=create_time, search=search)
                    db.session.add(new_section)
                    db.session.commit()
                    return redirect(f'/admindash')
                else:
                    return "SECTION ALREADY PRESENT"
            else:
                return "PLEASE FILL ALL THE FIELDS"

        return render_template('1.2_admin_add_section.html', admin=admin)
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"

@app.route('/addbook', methods=['GET', 'POST'])
@login_required	
def add_book():
    if current_user.user_type == 'admin':
        admin_id = current_user.id
        admin = Users.query.get(admin_id)
        if request.method == 'POST':
            book_name = request.form.get('book_name')
            authors_name = request.form.get('authors_name')

            if 'book' not in request.files:
                return "No File Uploaded"
            
            file = request.files['book']

            if file.filename == "":
                return "No File Selected"

            if file:
                filename = secure_filename(file.filename)

            
            if book_name and authors_name and filename:
                book_query = Books.query.filter_by(name=book_name).first()
                if not book_query:
                    if 'cover' in request.files and request.files['cover'].filename != "":
                        cover = request.files['cover']
                        covername = secure_filename(cover.filename)
                        cover.save(os.path.join(app.static_folder, "book_cover", covername))
                    else:
                        covername = "default.jpg"

                    search = search_string_convert(book_name+authors_name)
                    file.save(os.path.join(app.static_folder, "books", filename))
                    book_obj = Books(name=book_name, authors=authors_name, filename=filename, covername=covername , search = search)
                    db.session.add(book_obj)
                    db.session.commit()
                    return "BOOK UPLOADED SUCCESSFULLY"
                else:
                    return "BOOK ALREADY PRESENT"
            else:
                return "PLEASE FILL ALL THE FIELDS"
        return render_template('1.4_admin_add_book.html', admin=admin)
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"

@app.route('/addbooktothissection/<int:section_id>/<int:book_id>', methods=['GET', 'POST'])
@login_required	
def add_book_to_this_section(section_id, book_id):
    if current_user.user_type == 'admin':
        new_section_book_association = SectionsBooks(section_id=section_id, book_id=book_id)
        db.session.add(new_section_book_association)
        db.session.commit()
        return redirect(f'/editsection/{section_id}')
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"
    
@app.route('/addthisbooktosections/<int:section_id>/<int:book_id>', methods=['GET', 'POST'])
@login_required	
def add_this_book_to_section(section_id, book_id):
    if current_user.user_type == 'admin':
        new_section_book_association = SectionsBooks(section_id=section_id, book_id=book_id)
        db.session.add(new_section_book_association)
        db.session.commit()
        return redirect(f'/editbook/{book_id}')
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"


@app.route('/editsection/<int:section_id>', methods=['GET', 'POST'])
@login_required	
def edit_section(section_id):
    if current_user.user_type == 'admin':
        admin_id = current_user.id
        admin = Users.query.get(admin_id)
        section = Sections.query.get(section_id)
        books_in_this_section = [book for book in section.books if book.is_active==True]
        books_not_in_this_section = Books.query.filter(~Books.sections.any(Sections.id == section_id)).filter_by(is_active=True).all()
        if request.method == 'POST':
            section_name = request.form.get('section_name')
            description = request.form.get('description')

            if (not section_name and not description):
                return "PLEASE FILL DETAILS"

            section_query = Sections.query.filter_by(name=section_name).first()
            if section_query:
                return "SECTION ALREADY PRESENT"
            
            section = Sections.query.get(section_id)
            if section_name:
                section.name = section_name
                section.search = search_string_convert(section_name)
            if description:
                section.description = description

            db.session.commit()
            return redirect(f'/admindash')
        return render_template('1.2.1_admin_edit_section.html', admin=admin, section=section, books_in_this_section=books_in_this_section, books_not_in_this_section=books_not_in_this_section)
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"


@app.route('/editbook/<int:book_id>', methods=['GET', 'POST'])
@login_required	
def edit_book(book_id):
    if current_user.user_type == 'admin':
        admin_id = current_user.id
        admin = Users.query.get(admin_id)
        book = Books.query.get(book_id)
        sections_which_exclude_this_book = Sections.query.filter(~Sections.books.any(Books.id == book_id)).all()
        sections = Sections.query.all()
        if request.method == 'POST':
            book_name = request.form.get('book_name')
            authors_name = request.form.get('authors_name')

            if (not book_name and not authors_name):
                if 'book' in request.files and 'cover' in request.files:
                    file = request.files['book']
                    cover = request.files['cover']
                    if file.filename == "" and cover.filename == "":
                        return "PLEASE FILL DETAILS OR SELECT FILE"
                else:
                    return "PLEASE FILL ALL DETAILS"
                

            book_query = Books.query.filter_by(name=book_name).first()
            if book_query:
                return "BOOK ALREADY PRESENT"
            
            book = Books.query.get(book_id)
            if book_name:
                book.name = book_name
                book.search = search_string_convert(book_name+book.authors)
            if authors_name:
                book.authors = authors_name
                book.search = search_string_convert(book.name+authors_name)

            if 'book' in request.files :
                file = request.files['book']
                if file.filename != "":
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.static_folder, "books", filename))
                    book.filename = filename

            if 'cover' in request.files :
                cover = request.files['cover']
                if cover.filename != "":
                    covername = secure_filename(cover.filename)
                    cover.save(os.path.join(app.static_folder, "book_cover", covername))
                    book.covername = covername


            db.session.commit()
            return redirect(f'/admindash')
        return render_template('1.4.1_admin_edit_book.html', admin=admin, book=book , sections_which_exclude_this_book = sections_which_exclude_this_book, sections=sections)
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"



@app.route('/adminviewsection/<int:section_id>')
@login_required	
def admin_view_section(section_id):
    if current_user.user_type == 'admin':
        admin_id = current_user.id
        admin = Users.query.get(admin_id)
        admin = Users.query.filter_by(user_type='admin').first()
        section = Sections.query.get(section_id)

        section_active_books = [a for a in section.books if a.is_active == True]
        return render_template('1.3_admin_view_section.html', admin=admin, section=section, section_active_books=section_active_books)
    
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"

   
@app.route('/userviewsection/<int:section_id>')
@login_required	
def user_view_section(section_id):
    user_id = current_user.id
    this_user = Users.query.get(user_id)
    section = Sections.query.get(section_id)
    section_active_books = [a for a in section.books if a.is_active==True]
    issued_transactions = Transactions.query.filter_by(user_id=user_id).filter(Transactions.status == 'issued').all()
    issued_books = [trans.book for trans in issued_transactions]
    return render_template('2.3_user_view_section.html', this_user=this_user, section=section, section_active_books=section_active_books, issued_books=issued_books)

@app.route('/adminviewbook/<int:book_id>')
@login_required	
def admin_view_book(book_id):
    if current_user.user_type == 'admin':
        admin_id = current_user.id
        admin = Users.query.get(admin_id)
        book = Books.query.get(book_id)
        book_transaction_issued = Transactions.query.filter(and_(Transactions.book_id==book_id, Transactions.status=='issued')).first()

        book_transactions = [a for a in book.transactions if a.feedback != "no feedback"]
        return render_template('1.5_admin_view_book.html', admin=admin, book=book, book_transaction_issued=book_transaction_issued, book_transactions=book_transactions)
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"

@app.route('/userviewbook/<int:book_id>')
@login_required	
def user_view_book(book_id):
    user_id = current_user.id
    this_user = Users.query.get(user_id)
    book = Books.query.get(book_id)
    book_transactions = [a for a in book.transactions if a.feedback != "no feedback"]
    issued_transactions = Transactions.query.filter_by(user_id=user_id).filter(Transactions.status == 'issued').all()
    issued_books = [trans.book for trans in issued_transactions]
    return render_template('2.4_user_view_book.html', book=book , this_user=this_user, book_transactions=book_transactions, issued_books=issued_books)

@app.route('/read/<int:book_id>')
@login_required
def read(book_id):
    if current_user.user_type == 'admin':
        book = Books.query.get(book_id)
        return render_template("read.html", book=book)
    
    user_id = current_user.id
    this_user = Users.query.get(user_id)
    book = Books.query.get(book_id)
    issued_transactions = Transactions.query.filter_by(user_id=user_id).filter(Transactions.status == 'issued').all()
    issued_books = [trans.book for trans in issued_transactions]
    if book in issued_books:
        return render_template("read.html", this_user=this_user, book=book)
    else:
        return "YOU DON'T HAVE PERMISSION TO READ THIS BOOK"


@app.route('/deletesection/<int:section_id>')
@login_required	
def delete_section( section_id):
    if current_user.user_type == 'admin':
        section = Sections.query.get(section_id)
        sections_books_association = SectionsBooks.query.filter_by(section_id=section_id).all()
        db.session.delete(section)
        for i in sections_books_association:
            db.session.delete(i)
        db.session.commit()
        return redirect(f'/admindash')
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"

@app.route('/deletebook/<int:book_id>')
@login_required	
def delete_book(book_id):
    if current_user.user_type == 'admin':
        book = Books.query.get(book_id)
        sections_books_association = SectionsBooks.query.filter_by(book_id=book_id).all()
        book.is_active = False
        db.session.commit()
        return redirect(f'/admindash')
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"
    
@app.route('/removebookfromsectioninviewsection/<int:section_id>/<int:book_id>')
@login_required	
def remove_book_from_section_in_view_section(section_id, book_id):
    if current_user.user_type == 'admin':
        sections_books_association = SectionsBooks.query.filter_by(section_id=section_id, book_id=book_id).first()
        db.session.delete(sections_books_association)
        db.session.commit()
        return redirect(f'/adminviewsection/{section_id}')
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"
    
@app.route('/removebookfromsectionineditsection/<int:section_id>/<int:book_id>')
@login_required	
def remove_book_from_section_in_edit_section(section_id, book_id):
    if current_user.user_type == 'admin':
        admin_id = current_user.id
        admin = Users.query.get(admin_id)
        sections_books_association = SectionsBooks.query.filter_by(section_id=section_id, book_id=book_id).first()
        db.session.delete(sections_books_association)
        db.session.commit()
        return redirect(f'/editsection/{section_id}')
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"
    
@app.route('/mybooks', methods=['GET', 'POST'])
@login_required	
def my_books():
    user_id = current_user.id
    this_user = Users.query.get(user_id)
    issued_transactions = Transactions.query.filter_by(user_id=user_id).filter(Transactions.status == 'issued').all()
    now = datetime.now()

    for trans in issued_transactions:
        if trans.issue_date < (now-timedelta(days=trans.duration)):
            trans.status = 'revoked'
            trans.book.status = 'available'
    db.session.commit()

    issued_transactions = Transactions.query.filter_by(user_id=user_id).filter(Transactions.status == 'issued').all()
    issued_books = [trans.book for trans in issued_transactions]

    return render_template('2.2_user_my_books.html', this_user=this_user, active_issued_transactions=issued_transactions, issued_books=issued_books)


@app.route('/myrequests', methods=['GET', 'POST'])
@login_required	
def my_requests():
    user_id = current_user.id
    this_user = Users.query.get(user_id)
    user_trans = this_user.transactions
    user_requests = Transactions.query.filter_by(user_id=user_id).filter(Transactions.status == 'requested').all()
    return render_template('2.2.1_user_my_requests.html', this_user=this_user, user_requests=user_requests, user_trans=user_trans)


@app.route('/requestbook/<int:book_id>', methods=['GET', 'POST'])
@login_required	
def request_book(book_id):
    user_id = current_user.id
    this_user = Users.query.get(user_id)
    user_active_trans = Transactions.query.filter_by(user_id=user_id).filter(Transactions.status.in_(['requested', 'issued'])).all()
    already_requested = Transactions.query.filter_by(user_id=user_id, book_id=book_id).filter(Transactions.status == 'requested').all()

    if already_requested:
        return "BOOK ALREADY REQUESTED"
    elif len(user_active_trans) < this_user.max_books_allowed:
        book = Books.query.get(book_id)
        user = Users.query.get(user_id)
        if book.status == 'available':
            request_time = datetime.now()
            new_trans = Transactions(request_date=request_time, user_id=user_id, book_id=book_id)
            db.session.add(new_trans)
            db.session.commit()
            return "REQUEST SUCCESSFULL"
        else:
                return "BOOK NOT AVAILABLE"
    else:
        return "CANNOT REQUEST MORE THAN THREE BOOKS"


@app.route('/returnbook/<int:trans_id>')
@login_required	
def return_book(trans_id):
    user_id = current_user.id
    transaction = Transactions.query.get(trans_id)
    return_time = datetime.now()
    if transaction.user_id == user_id:
        transaction.status = 'returned'
        transaction.return_date = return_time
        transaction.book.status = 'available'
        db.session.commit()
    return redirect(f'/mybooks')


@app.route('/feedback/<int:trans_id>', methods=['GET', 'POST'])
@login_required	
def give_feedback(trans_id):
    user_id = current_user.id
    this_user = Users.query.get(user_id)
    transaction = Transactions.query.get(trans_id)
    if request.method == 'POST':
        feedback = request.form.get('feedback')
        if transaction.user_id == user_id:
            transaction.feedback = feedback
            db.session.commit()
        return redirect(f'/mybooks')

    return render_template("2.4.1_user_feedback.html", this_user=this_user, transaction=transaction)



@app.route('/checkrequests', methods=['GET', 'POST'])
@login_required	
def check_requests():
    if current_user.user_type == 'admin':
        admin_id = current_user.id
        admin = Users.query.get(admin_id)
        requested_trans = Transactions.query.filter_by(status='requested').all()
        issued_trans = Transactions.query.filter_by(status='issued').all()
        return render_template('1.6_admin_check_requests.html', admin=admin, requested_trans=requested_trans, issued_trans=issued_trans)
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"    

@app.route('/transactionshistory', methods=['GET', 'POST'])
@login_required	
def transactions_history():
    if current_user.user_type == 'admin':
        admin_id = current_user.id
        admin = Users.query.get(admin_id)
        transactions = Transactions.query.all()
        return render_template('1.7_admin_transactions_history.html', admin=admin, transactions=transactions)
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"   


@app.route('/viewusers', methods=['GET', 'POST'])
@login_required	
def check_users():
    if current_user.user_type == 'admin':
        admin_id = current_user.id
        admin = Users.query.get(admin_id)
        users = Users.query.all()
        return render_template('1.7.0_admin_view_users.html', admin=admin, users=users)
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"   


@app.route('/viewuserrequests/<int:user_id>', methods=['GET', 'POST'])
@login_required	
def view_user_requests(user_id):
    if current_user.user_type == 'admin':
        admin_id = current_user.id
        admin = Users.query.get(admin_id)
        this_user = Users.query.get(user_id)
        transactions = Transactions.query.filter_by(user_id=user_id).filter(or_(Transactions.status=='requested', Transactions.status=='issued')).all()
        return render_template('1.7.2_admin_view_users_requests.html', admin=admin, this_user=this_user, transactions=transactions)
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE" 

@app.route('/viewusertrans/<int:user_id>', methods=['GET', 'POST'])
@login_required	
def view_user_trans(user_id):
    if current_user.user_type == 'admin':
        admin_id = current_user.id
        admin = Users.query.get(admin_id)
        this_user = Users.query.get(user_id)
        transactions = this_user.transactions
        return render_template('1.7.1_admin_view_users_trans.html', admin=admin, this_user=this_user, transactions=transactions)
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"

@app.route('/deactivateuser/<int:user_id>/<string:action>', methods=['GET', 'POST'])
@login_required	
def deactivate_user(user_id, action):
    if current_user.user_type == 'admin':
        admin_id = current_user.id
        admin = Users.query.get(admin_id)
        this_user = Users.query.get(user_id)
        if action == 'activate':
            this_user.is_active = True
        else:
            this_user.is_active = False
        db.session.commit()
        return redirect(f"/viewusers")
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"



@app.route('/adminstats', methods=['GET', 'POST'])
@login_required	
def admin_stats():
    if current_user.user_type == 'admin':
        admin_id = current_user.id
        admin = Users.query.get(admin_id)
        sections = Sections.query.all()

        if sections:
            categories1 = [a.name for a in sections]
            values1 = []
            for section in sections:
                a = Books.query.join(SectionsBooks).join(Sections).filter(and_(Sections.id==section.id, Books.is_active==True, Books.status=='unavailable')).count()
                values1.append(a)

            plt.figure(figsize=(6, 4))
            plt.bar(categories1, values1)
            plt.xlabel('Categories')
            plt.ylabel('Values')
            plt.title('Issued Books')
            plt.yticks(range(0, max(values1) + 1))
            plt.tight_layout()
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            chart_image1 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()
        else:
            chart_image1 = False


        if sections:
            categories2 = [a.name for a in sections]
            values2 = []
            for section in sections:
                a = Books.query.join(SectionsBooks).join(Sections).filter(and_(Sections.id==section.id, Books.is_active==True)).count()
                values2.append(a)

            plt.figure(figsize=(5, 5))
            plt.pie(values2, labels=categories2, autopct='%1.1f%%')
            plt.title('Section-wise Books Distribution')
            plt.axis('equal')

            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            chart_image2 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()
        else:
            chart_image2 = False


        return render_template("1.8_admin_stats.html", admin=admin, chart_image1=chart_image1, chart_image2=chart_image2)
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"







@app.route('/userstats', methods=['GET', 'POST'])
@login_required	
def user_stats():
    user_id = current_user.id
    this_user = Users.query.get(user_id)


    sections = Sections.query.all()
    if sections:
        categories1 = [a.name for a in sections]
        values1 = []
        for section in sections:
            a = Books.query.join(SectionsBooks).join(Sections).filter(and_(Sections.id==section.id, Books.is_active==True, Books.status=='available')).count()
            values1.append(a)

        plt.figure(figsize=(6, 4))
        plt.bar(categories1, values1)
        plt.xlabel('Categories')
        plt.ylabel('Values')
        plt.title('Available Books')
        plt.yticks(range(0, max(values1) + 1))
        plt.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        chart_image1 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
    else:
        chart_image1=False





    this_user_trans = this_user.transactions
    if this_user_trans:
        categories2 = ['requested', 'issued', 'rejected', 'returned', 'revoked']
        x = {'requested':0, 'issued':0, 'rejected':0, 'returned':0, 'revoked':0}
        for trans in this_user_trans:
            if trans.status in categories2:
                x[trans.status] = x[trans.status] + 1

        values2 = []
        for a in categories2:
            values2.append(x[a])

        plt.figure(figsize=(5, 5))
        plt.pie(values2, labels=categories2, autopct='%1.1f%%')
        plt.title('My Transactions Distribution')
        plt.axis('equal')

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        chart_image2 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
    else:
        chart_image2=False



    return render_template("2.6_user_stats.html", this_user=this_user, chart_image1=chart_image1, chart_image2=chart_image2)








@app.route('/grant/<int:trans_id>', methods=['GET', 'POST'])
@login_required	
def grant(trans_id):
    if current_user.user_type == 'admin':
        admin_id = current_user.id
        admin = Users.query.get(admin_id)
        transaction = Transactions.query.get(trans_id)
        issue_time = datetime.now()
        transaction.status = 'issued'
        transaction.issue_date = issue_time
        transaction.book.status = 'unavailable'
        db.session.commit()
        return redirect(f'/checkrequests')
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"

@app.route('/reject/<int:trans_id>', methods=['GET', 'POST'])
@login_required	
def reject(trans_id):
    if current_user.user_type == 'admin':
        admin_id = current_user.id
        admin = Users.query.get(admin_id)
        transaction = Transactions.query.get(trans_id)
        transaction.status = 'rejected'
        transaction.book.status = 'available'
        db.session.commit()
        return redirect(f'/checkrequests')
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"

@app.route('/revoke/<int:trans_id>', methods=['GET', 'POST'])
@login_required	
def revoke(trans_id):
    if current_user.user_type == 'admin':
        admin_id = current_user.id
        admin = Users.query.get(admin_id)
        books = Books.query.all()
        transaction = Transactions.query.get(trans_id)
        revoke_time = datetime.now()
        transaction.status = 'revoked'
        transaction.revoke_date = revoke_time
        if transaction.book_id:
            transaction.book.status = 'available'
        db.session.commit()
        return redirect(f'/checkrequests')
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"




@app.route('/grantforuser/<int:user_id>/<int:trans_id>', methods=['GET', 'POST'])
@login_required	
def grant_for_user(user_id, trans_id):
    if current_user.user_type == 'admin':
        admin_id = current_user.id
        admin = Users.query.get(admin_id)
        transaction = Transactions.query.get(trans_id)
        issue_time = datetime.now()
        transaction.status = 'issued'
        transaction.date_issued = issue_time
        transaction.book.status = 'unavailable'
        db.session.commit()
        return redirect(f'/viewuserrequests/{user_id}')
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"

@app.route('/rejectforuser/<int:user_id>/<int:trans_id>', methods=['GET', 'POST'])
@login_required	
def reject_for_user(user_id, trans_id):
    if current_user.user_type == 'admin':
        admin_id = current_user.id
        admin = Users.query.get(admin_id)
        transaction = Transactions.query.get(trans_id)
        transaction.status = 'rejected'
        transaction.book.status = 'available'
        db.session.commit()
        return redirect(f'/viewuserrequests/{user_id}')
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"

@app.route('/revokeforuser/<int:user_id>/<int:trans_id>', methods=['GET', 'POST'])
@login_required	
def revoke_for_user(user_id, trans_id):
    if current_user.user_type == 'admin':
        admin_id = current_user.id
        admin = Users.query.get(admin_id)
        transaction = Transactions.query.get(trans_id)
        revoke_time = datetime.now()
        transaction.status = 'revoked'
        transaction.revoke_date = revoke_time
        transaction.book.status = 'available'
        db.session.commit()
        return redirect(f'/viewuserrequests/{user_id}')
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"



@app.route('/adminsearch', methods=['GET', 'POST'])
@login_required	
def admin_search():
    if current_user.user_type == 'admin':
        admin_id = current_user.id
        admin = Users.query.get(admin_id)
        search_query = request.form.get('search_query')

        searched_sections = Sections.query.filter(or_(Sections.name.ilike(f'%{search_query}%'), Sections.search.ilike(f'%{search_query}%'))).all()
        searched_books = Books.query.filter(or_(Books.name.ilike(f'%{search_query}%'), Books.authors.ilike(f'%{search_query}%'), Books.search.ilike(f'%{search_query}%'))).filter_by(is_active=True).all()
        searched_users = Users.query.filter(Users.username.ilike(f'%{search_query}%')).all()

        return render_template('1.7.9_admin_search.html', admin=admin, searched_sections=searched_sections, searched_books=searched_books, searched_users=searched_users)
    else:
        return "YOU DON'T HAVE PERMISSION TO VIEW THIS PAGE"

@app.route('/usersearch', methods=['GET', 'POST'])
@login_required	
def user_search():
    user_id = current_user.id
    this_user = Users.query.get(user_id)
    issued_transactions = Transactions.query.filter_by(user_id=user_id).filter(Transactions.status == 'issued').all()
    issued_books = [trans.book for trans in issued_transactions]

    search_query = request.form.get('search_query')

    searched_sections = Sections.query.filter(or_(Sections.name.ilike(f'%{search_query}%'), Sections.search.ilike(f'%{search_query}%'))).all()
    searched_active_books = Books.query.filter(or_(Books.name.ilike(f'%{search_query}%'), Books.authors.ilike(f'%{search_query}%'), Books.search.ilike(f'%{search_query}%'))).filter_by(is_active=True).all()
    
    return render_template('2.5_user_search.html', this_user=this_user, searched_sections=searched_sections, searched_active_books=searched_active_books, issued_books=issued_books)






@app.errorhandler(401)
def unauthorized_access(error):
    return render_template('unauthorized.html'), 401











@app.route('/rough', methods=['GET', 'POST'])
def rough():
    if request.method == "POST":
        abc = "YESSS"

    abc = "NOOO"
    return render_template("rough.html", abc=abc)




def search_string_convert(a):
  b = a.split()
  c = ""
  for i in b:
    c = c + i.lower()
  return c