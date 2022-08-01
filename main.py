"""
Uzduotys:
1.(3) Surasti, isvardinti ir pataisyti visas projekte rastas klaidas zemiau, uz bent 5 rastas ir pataisytas pilnas balas:
    a) Nebuvo last_name formoje ir priskirta user, kad duomenys nukeliautų į duomenų bazę
    b) Klasėje User nebuvo panaudotas Mixin
    c) sign_in nebuvo methods=['GET', 'POST']
    d) user sign_in page buvo atpažįstamas pagal first_name, o turi būti pagal email_address
    e) update_account_information formoje buvo naudojama form_in_html, o buvo prie route parašyta form=form, nors turi būti form_in_html=form
    f) Prie sign_out nebuvo parašytas logout_user()
    g) Prie update_account_information buvo panaudotas neteisingas method, reikėjo naudoti method=='GET', bei prie current_user visur buvo priskirta duomenų reikšmė email_address
    h) Puslapyje Update account info užrašas buvo Sign up, nors turėtų būti update account info
2.(7) Praplesti aplikacija i bibliotekos resgistra pagal apacioje surasytus reikalavimus:
    a)(1) Naudojant SQLAlchemy klases, aprasyti lenteles Book, Author su pasirinktinais atributais su tinkamu rysiu -
        vienas autorius, gali buti parases daug knygu, ir uzregistruoti juos admin'e
    b)(2) Sukurti (papildomus) reikiamus rysius tarp duombaziniu lenteliu, kad atitiktu zemiau pateiktus reikalavimus
    c) Sukurti puslapius Available Books ir My Books:
        i)(2) Available Books puslapis
            - isvesti bent knygos pavadinima ir autoriu
            - turi buti prieinamas tik vartotojui prisijungus,
            - rodyti visas knygas, kurios nera pasiskolintos
            - tureti mygtuka ar nuoroda "Borrow" prie kiekvienos knygos, kuri/ia paspaudus, knyga yra priskiriama
              varototojui ir puslapis perkraunamas
              (del paprastumo, sakome kad kiekvienos i sistema suvestos knygos turima lygiai 1)
        ii)(2) My Books puslapis
            - turi matytis ir buti prieinamas tik vartotojui prisijungus
            - rodyti visas knygas, kurios yra pasiskolintos prisijungusio vartotojo
            - salia kiekvienos knygos mygtuka/nuoroda "Return", kuri/ia paspaudus, knyga grazinama i biblioteka ir
              perkraunamas puslapis
    f)(2) Bonus: praplesti aplikacija taip, kad bibliotekoje kiekvienos knygos galetu buti
        daugiau negu vienas egzempliorius//
Pastabos:
    - uzstrigus su pirmaja uzduotimi, galima paimti musu paskutini flask projekto template
        ir ten atlikti antra uzduoti
    - nereikalingus templates geriau panaikinti ar persidaryti, kaip reikia. Tas pats galioja su MyTable klase
    - antram vartotojui prisijungus, nebeturi matytis kyngos, kurios buvo pasiskolintos pirmojo vartotojo
        nei prie Available Books, nei prie My Books
    - visam administravimui, pvz. knygu suvedidimui galima naudoti admin
    - sprendziant bonus uzduoti, apsvarstyti papildomos lenteles isivedima
"""

from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_bcrypt import Bcrypt
from flask_login import AnonymousUserMixin, LoginManager, login_user, current_user, login_required, UserMixin, \
    logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import forms

app = Flask(__name__)


class MyAnonymousUserMixin(AnonymousUserMixin):
    is_admin = False


login_manager = LoginManager(app)

login_manager.login_view = 'sign_in'
login_manager.login_message = 'Please login to access this page.'
login_manager.login_message_category = 'info'
login_manager.anonymous_user = MyAnonymousUserMixin

admin = Admin(app)

bcrypt = Bcrypt(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '(/("ZOHDAJK)()kafau029)ÖÄ:ÄÖ:"OI§)"Z$()&"()!§(=")/$'

db = SQLAlchemy(app)

Migrate(app, db)

association_table = db.Table('association_authors_books', db.metadata,
                             db.Column('book_id', db.Integer, db.ForeignKey('book.id')),
                             db.Column('author_id', db.Integer, db.ForeignKey('author.id')))

association_table_1 = db.Table('association_users_books', db.metadata,
                               db.Column('book_id', db.Integer, db.ForeignKey('book.id')),
                               db.Column('user_id', db.Integer, db.ForeignKey('user.id')))


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Integer, nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email_address = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    books = db.relationship('Book', secondary=association_table_1, back_populates='users')

    def __repr__(self):
        return f'{self.first_name} {self.last_name}'


class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(13), nullable=False)
    genre = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    authors = db.relationship('Author', secondary=association_table, back_populates='books')
    users = db.relationship('User', secondary=association_table_1, back_populates='books')


class Author(db.Model):
    __tablename__ = 'author'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    books = db.relationship('Book', secondary=association_table, back_populates='authors')

    def __repr__(self):
        return f'{self.first_name} {self.last_name}'


db.create_all()


class MyModelView(ModelView):

    def is_accessible(self):
        return current_user.is_admin


admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Book, db.session))
admin.add_view(MyModelView(Author, db.session))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/my_books', methods=['GET', 'POST'])
def my_books():
    data = Book.query.all()
    return render_template('my_books.html', data=data)


@app.route('/show', methods=['GET', 'POST'])
@login_required
def show():
    data = Book.query.all()
    return render_template('show.html', data=data)


@app.route('/borrow_book/<id>')
@login_required
def borrow_book(id):
    user = User.query.filter_by(id=current_user.id).first()
    book = Book.query.filter_by(id=id).first()
    if not user.books:
        book.quantity -= 1
        book.users.append(user)
        db.session.add(book)
        db.session.commit()
        flash(f'You have successfully borrowed a book!', 'success')
        return redirect(url_for('show'))
    else:
        is_borrowed = list(filter(lambda x: x == book, user.books))
        if not is_borrowed:
            book.quantity -= 1
            book.users.append(user)
            db.session.add(book)
            db.session.commit()
            flash('You have successfully borrowed a book!', 'success')
            return redirect(url_for('show'))
        else:
            print(is_borrowed)
            flash('You already have this book!', 'danger')
            return redirect(url_for('show'))


@app.route('/return_book/<id>')
@login_required
def return_book(id):
    book = Book.query.filter_by(id=id).first()
    user = User.query.filter_by(id=current_user.id).first()
    book.users.remove(user)
    book.quantity += 1
    db.session.add(book)
    db.session.commit()
    flash('You have successfully returned a book!', 'success')
    return redirect(url_for('my_books'))


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = forms.SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password1.data).decode()
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email_address=form.email_address.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Welcome, {current_user.first_name}', 'success')
        return redirect(url_for('home'))
    return render_template('sign_up.html', form=form)


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    form = forms.SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email_address.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f'Welcome, {current_user.first_name}', 'success')
            return redirect(request.args.get('next') or url_for('home'))
        flash(f'User or password does not match', 'danger')
        return render_template('sign_in.html', form=form)
    return render_template('sign_in.html', form=form)


@app.route('/update_account_information', methods=['GET', 'POST'])
def update_account_information():
    form = forms.UpdateAccountInformationForm()
    if request.method == 'GET':
        form.email_address.data = current_user.email_address
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
    if form.validate_on_submit():
        current_user.email_address = form.email_address.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        db.session.commit()
        flash('User information updated', 'success')
        return redirect(url_for('update_account_information'))
    return render_template('update_account_information.html', form_in_html=form)


@app.route('/sign_out')
def sign_out():
    logout_user()
    flash('Goodbye, see you next time', 'success')
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
