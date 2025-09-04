import datetime, uuid

# user-related classes

class User: # abstract class
    maxBorrowDays = 0
    maxBooks = 0

    def __init__(self, name, email, userId):
        self.name = name
        self.email = email
        self.userId = userId # should store that thing in sqlite db
        self.borrowedBooks = []

    def canBorrow(self):
        return len(self.borrowedBooks) < self.maxBooks

class Student(User):
    maxBorrowDays = 14
    maxBooks = 3

class Faculty(User):
    maxBorrowDays = 30
    maxBooks = 10

class Guest(User):
    maxBorrowDays = 7
    maxBooks = 1

# supporting classes

class Book:

    def __init__(self, title, author, genre, isbn):
        self.title = title
        self.author = author
        self.genre = genre
        self.isbn = isbn
        self._available = True
    
    def isAvailable(self):
        return self._available

class BorrowingRecord:

    def __init__(self, user, book, date):
        self.user = user
        self.book = book
        self.date = date
        self.returnDate = None

# main class

class Library:

    def __init__(self):
        self._books = {} # isbn -> book
        self._users = {} # userId -> user
        self._borrowingHistory = []


    def addBook(self, book):
        if book.isbn in self._books:
            return False, f"ISBN {book.isbn} already exists."
        else:
            self._books[book.isbn] = book
            return True, f'Book {book.isbn} added successfully.'


    def removeBook(self, isbn):
        if isbn in self._books:
            del self._books[isbn]
            return True, 'Book removed successfully'
        else:
            return False, f"ISBN {isbn} does not exist."


    def findBook(self, isbn):
        return self._books.get(isbn, None)


    def searchBooks(self, query: str):
        query = query.lower()
        res = []
        for book in self._books.values():
            if (query in book.title.lower()
                or query in book.author.lower()
                or query in book.genre.lower()
                or query in book.isbn.lower()):
                res.append(book)
        return res



    def registerUser(self, name, email, userId, type: int):
        if userId in self._users:
            return None, f"User {userId} already exists."
        else:
            if type == 1:
                user = Student(name, email, userId)
            elif type == 2:
                user = Faculty(name, email, userId)
            elif type == 3:
                user = Guest(name, email, userId)
            else:
                return None, "Invalid user type."
            self._users[userId] = user
            return user, f"User {user.userId} successfully registered."


    def findUser(self, userId):
        return self._users.get(userId, None)



    def borrowBook(self, userId, isbn):
        user = self.findUser(userId)
        if user is None:
            return False, f"User {userId} does not exist."

        book = self.findBook(isbn)
        if book is None:
            return False, f"Book {isbn} does not exist."

        if not user.canBorrow():
            return False, 'You cannot borrow more books.'

        if not book.isAvailable():
            return False, 'Book is unavailable.'

        book._available = False
        user.borrowedBooks.append(isbn)
        self._borrowingHistory.append(BorrowingRecord(user, book, datetime.datetime.now()))
        return True, f'Book {isbn} has successfully been borrowed.'


    def returnBook(self, userId, isbn):
        user = self.findUser(userId)
        if user is None:
            return False, f"User {userId} does not exist."

        book = self.findBook(isbn)
        if book is None:
            return False, f"Book {isbn} does not exist."

        if isbn not in user.borrowedBooks:
            return False, 'Book is not borrowed by this user.'

        for record in reversed(self._borrowingHistory):
            if record.user == user and record.book == book and record.returnDate is None:
                record.returnDate = datetime.datetime.now()
                user.borrowedBooks.remove(isbn)
                book._available = True
                return True, f'Book {isbn} has successfully been returned.'
        return False, 'Borrowing record not found (maybe already returned).'


    def getOverdueBooks(self):
        res = []
        for record in self._borrowingHistory:
            if record.returnDate is None and datetime.datetime.now() - record.date > datetime.timedelta(days=record.user.maxBorrowDays):
                res.append(record)
        return res

# console interface

class LibConsole:

    def __init__(self):
        self.lib = Library()
        self.running = True
  

    def displayMenu(self): # main menu
        print("\n=== Library Management ===")
        print("1. Book Management")
        print("2. User Management")
        print("3. Borrowing Operations")
        print("0. Exit")


    def getChoice(self, maxval, minval=0):
        while float('inf') + 1 == float('inf'):
            try:
                choice = int(input('Choose an action (integer): '))
                if minval <= choice <= maxval:
                    return choice
                else:
                    raise ValueError
            except ValueError:
                print('Invalid choice')


    def run(self):
        while self.running:
            self.displayMenu()
            choice = self.getChoice(3)

            if choice == 1:
                self.handleBookManagement()                    
            elif choice == 2:
                self.handleUserManagement()
            elif choice == 3:
                self.handleBorrowingOperations()
            elif choice == 0:
                self.running = False
            else:
                print('Incorrect choice')

    # book management

    def handleBookManagement(self):
        print("\n--- Book Management ---")
        print("1. Add book")
        print("2. Remove book")
        print("3. Find book")
        print("4. Search books")
        print("0. Back")

        choice = self.getChoice(4)

        if choice == 1:
            self.handleAddBook()

        elif choice == 2:
            isbn = str(input('Enter isbn: '))
            success, msg = self.lib.removeBook(isbn)
            print(msg)

        elif choice == 3:
            isbn = str(input('Enter isbn: '))
            book = self.lib.findBook(isbn)
            if book is not None:
                print('\nFound book:')
                self.bookHandler(book)
            else:
                print(f"Book {isbn} does not exist.")

        elif choice == 4:
            query = str(input('Enter query: '))
            result = self.lib.searchBooks(query)
            if result:
                for i, book in enumerate(result):
                    print(f'\n{i}) Book {book.isbn}:')
                    self.bookHandler(book)
            else:
                print("No books found matching the query.")

        elif choice == 0:
            return


    def handleAddBook(self):
        title = str(input('Enter title: '))
        author = str(input('Enter author: '))
        genre = str(input('Enter genre: '))
        isbn = str(input('Enter isbn: '))
        book = Book(title, author, genre, isbn)
        success, msg = self.lib.addBook(book)
        print(msg)
        if success:
            self.bookHandler(book)


    def bookHandler(self, book): # prints info about an instance of the Book class
        print(f'{book.title} by {book.author}')
        print(f'Genre: {book.genre}')


    # user management

    def handleUserManagement(self):
        print("\n--- User Management ---")
        print("1. Register User")
        print("2. Find User")
        print("0. Back")

        choice = self.getChoice(2)

        if choice == 1:
            self.handleAddUser()

        elif choice == 2:
            userId = str(input('Enter userId: '))
            user = self.lib.findUser(userId)
            if user is not None:
                print('\nFound user:')
                self.userHandler(user)
            else:
                print(f"User {userId} does not exist.")

        elif choice == 0:
            return


    def handleAddUser(self):
        name = str(input('Enter name: '))
        email = str(input('Enter email: '))
        userId = str(uuid.uuid4())[:8] # just a placeholder (maybe)
        print('Choose a user type. User types:\n1 - Student\n2 - Faculty\n3 - Guest')
        type = self.getChoice(3, 1)
        user, msg = self.lib.registerUser(name, email, userId, type)
        print(msg)
        if user is not None:
            self.userHandler(user)


    def userHandler(self, user): # prints info about an instance of the User class
        print(f'Name: {user.name}')
        print(f'Email: {user.email}')


    # borrowing operations

    def handleBorrowingOperations(self):
        print("\n--- Borrowing Operations ---")
        print("1. Borrow book")
        print("2. Return book")
        print("3. Overdue books")
        print("0. Back")

        choice = self.getChoice(3)

        if choice == 1:
            self.handleBorrowAndReturn(choice)

        elif choice == 2:
            self.handleBorrowAndReturn(choice)

        elif choice == 3:
            self.handleOverdueBooks()

        elif choice == 0:
            return


    def handleBorrowAndReturn(self, n): # n == 1 -> borrow; n == 2 -> return
        userId = str(input('Enter userId: '))
        isbn = str(input('Enter isbn: '))

        if n == 1:
            success, msg = self.lib.borrowBook(userId, isbn) # success might be used later for smth idk
        else:
            success, msg = self.lib.returnBook(userId, isbn)

        print(msg)


    def handleOverdueBooks(self):
        records = self.lib.getOverdueBooks()
        if not records:
            print("No overdue books at the moment.")
            return

        for i, record in enumerate(records):
            print(f'\n{i}) RECORD:')
            print('[BOOK]')
            self.bookHandler(record.book)
            print('[USER]')
            self.userHandler(record.user)
            print('[TIME SINCE THE OVERDUE]')
            overdue_time = datetime.datetime.now() - (record.date + datetime.timedelta(days=record.user.maxBorrowDays))
            print(overdue_time)



if __name__ == '__main__':
    console = LibConsole()
    console.run()