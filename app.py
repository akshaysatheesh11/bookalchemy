from flask import Flask, render_template, request, redirect, url_for, flash
from data_models import db, Author, Book

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/library.sqlite'
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a real secret key for production
db.init_app(app)


# Home route to display books
@app.route('/')
def home():
    books = Book.query.all()
    return render_template('home.html', books=books)


# Add author route
@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form['name']
        birth_date = request.form['birth_date']
        date_of_death = request.form['date_of_death']

        new_author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(new_author)
        db.session.commit()

        flash('Author added successfully!', 'success')
        return redirect(url_for('add_author'))

    return render_template('add_author.html')


# Add book route
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        isbn = request.form['isbn']
        publication_year = request.form['publication_year']
        author_id = request.form['author_id']

        new_book = Book(title=title, isbn=isbn, publication_year=publication_year, author_id=author_id)
        db.session.add(new_book)
        db.session.commit()

        flash('Book added successfully!', 'success')
        return redirect(url_for('add_book'))

    authors = Author.query.all()
    return render_template('add_book.html', authors=authors)


# Search books route
@app.route('/search', methods=['GET'])
def search_books():
    keyword = request.args.get('keyword')
    books = Book.query.filter(
        (Book.title.ilike(f'%{keyword}%')) |
        (Author.name.ilike(f'%{keyword}%'))
    ).join(Author).all()

    if not books:
        flash('No books found matching the search criteria', 'warning')

    return render_template('home.html', books=books)


# Delete book route
@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()

    # Check if the author has other books
    author = Author.query.get(book.author_id)
    if not Book.query.filter_by(author_id=author.id).all():
        db.session.delete(author)
        db.session.commit()

    flash('Book deleted successfully!', 'success')
    return redirect(url_for('home'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
