# Library Management System
### Description
This project aims to develop a Library Management System which enables a Librarian to manage books, sections and users, while Readers can register, login, request books, and provide feedback.

### Objectives
Create a user-friendly interface for librarian and Users. Implement functionalities for managing
sections, books, users, transactions. Implemet Login Functionality and CRUD APIs. Generate insightful
visualizations.

### Project Goals
Demonstrate Database Systems and Model-View-Controller Architecture understanding.

### Frameworks and libraries
- **Flask** : Micro web framework for building web applications in Python.
- **Flask-SQLAlchemy** : for database management, it simplifies database interactions.
- **Flask-RESTful** : for creating RESTful APIs.
- **Flask-Login** : Provides user session management, authentication, and authorization.
- **Matplotlib** : Python plotting library for creating graphs.

### Procedures
- First wrote the requirements and used Entity Relationship Model for defining entities and their relationships
- then created basic templates and Database Model.
- Implemented Flask App Structure and connected different modules.
- Added endpoints and business logic in controllers one at a time.
- Refined the models as more functionalities were added.

### Future Improvements
JWT authorization for APIs, data validation for forms, error Handling for API's, JavaScript
for client-side efficiency.


# Features
### Librarian
- can create, view, update, delete sections and books.
- can activate and deactivate users.
- can see requests and issued books.
- can grant, reject and revoke access of book.
- can see if the book is available or not, if not then to whom it is issued.
- can see all transactions.
- can see requests and all transactions of a particular user.
- can see section-wise bar graph of issued books and pie chart of Section-wise books distribution.
- can search sections, books and users.

### Users
- can view books and sections.
- can request, read and return books.
- can see my books and can give feedback for issued book.
- can see pending requests and all past transactions.
- can see section-wise bar graph of availabe books and pie chart of past transactions distribution.
- can search sections and books.

### Other
- autorevoke after n days, n can be changed for a particular user.
- added max books allowed per user, no. of max books can be changed for a particular user.
- added CRUD APIs for sections.
- added flask login.


# Architecture
### Data Base Design
- After Analysing the real world requirements, Entity Relationship Model is used for defining entities
and relationships among them.
- Primary keys are used to make Database in Third Normal Form.
- Database integrity is maintained using primary keys and foreign keys.
- Appropriate domain types are used for attributes to maintain data integrity and consistency.

### Presentation Layer
- Application Uses HTML templates for structure and Bootstrap for aesthetics, dynamic content is
rendered into templates using logic and endpoints in flask app.
- Matplotlib is used to plot graphs by using data from database

### Business Logic
- Transactions are implemented by updating and retrieving data from database using Flask-
SQLAlchemy queries
- all the endpoints are secured from unauthorized access using flask-login
- apis are implemented for performing CRUD operations

### Data Models
The data models are implemented in SQLite using SQLAlchemy.
- **Users**: Representing librarian and general users with attributes like username, password, user_type,
is_active, max_books_allowed.
- **Transactions**: Tracks borrowing and returning of books with attributes like id, user_id, book_id,
duration, request_date, return_date, feedback, etc.
- **Books**: For storing information about books and their authors with attributes like name, authors,
status, is_active, etc
- **Sections**: For managing different categories in the library with attributes like name, description,
date_created, etc.
- **Sections_Books**: This is a association table for many to many relationship between sections and
books.


## ➢ Conclusion
- Demonstrates Flask App structure, Database Model and MVC understanding.
- Future enhancements aim for data validation, security, error handling and user experience.

