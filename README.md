# Budget Helper
#### Video Demo:  https://youtu.be/-w6fpVWmTBM?si=I63iHzPnxN37sPZY
#### Description:
Budget Helper is a web application designed to assist users in managing their finances by providing tools for creating, viewing, editing, and deleting monthly budget plans. The application leverages modern web technologies and adheres to best practices for security and usability.

## Features
- **User Registration and Authentication**: Users can register for an account, log in, log out, and manage their profile.
- **Password Management**: Users can change their passwords or reset them to a default secure password.
- **Budget Management**: Users can create new budget plans, view existing ones, edit details, and delete plans if necessary.
- **Responsive Design**: The application is designed to be fully responsive, ensuring usability on both desktop and mobile devices.
- **Print Functionality**: The application allows users to easily print their montly budget.

## Project Structure
The project is organized into several key files and directories:

- **app.py**: The main application file that sets up routes and handles HTTP requests and responses.
- **user.py**: Contains functions related to user authentication and management, such as registering, logging in, and changing passwords.
- **budget.py**: Contains functions related to budget creation, viewing, editing, and deletion.
- **templates/**: This directory contains the HTML templates used to render the web pages.
  - **layout.html**: The base layout for the web application, including the header, footer, and main content area.
  - **index.html**: The homepage of the application.
  - **login.html**: The login page for user authentication.
  - **register.html**: The registration page for new users.
  - **change_password.html**: The page for changing a user's password.
  - **delete.html**: The confirmation page for user account deletion.
  - **budget.html**: The page for creating budget plans.
  - **view.html**: The page for viewing budget plans.
  - **edit.html**: The page for editing or deleting budget plans.
  - **error.html**: The error page displayed for various errors when flash isn't used.
- **static/**: This directory contains static files such as CSS and JavaScript.
  - **styles.css**: The main stylesheet for the application, ensuring a consistent look and feel.
- **budget.db**: The SQLite database file that stores user data and budget information.

## Design Choices
### Security
The following security measures have been implemented:
- **Password Hashing**: User passwords are hashed using `bcrypt` before being stored in the database. This ensures that even if the database is compromised, the passwords remain secure.
- **Input Validation**: User inputs are validated to prevent common security vulnerabilities such as SQL injection and cross-site scripting (XSS).
- **Session Management**: Secure session management practices are followed to protect user sessions.

### Responsiveness
To ensure the application is accessible on a variety of devices, the layout is designed using Bootstrap's responsive grid system. This ensures that the content adjusts dynamically based on the screen size, providing a seamless experience on both mobile and desktop devices.

### User Experience
The user experience is prioritized through:
- **Intuitive Navigation**: The navigation bar provides quick access to all major functionalities, ensuring users can easily find what they need.
- **Feedback Messages**: The application provides feedback messages for various actions (e.g., successful registration, errors during login) to keep the user informed.
- **Consistent Design**: A consistent design is maintained across all pages to provide a cohesive and professional appearance.
- **Portable Design**: The application is designed to be easily used on both desktop as well as mobile devices.

## Functionality
### User Registration
Users can register by providing their name, username, and a password. The password must meet specific criteria (minimum 8 characters, containing uppercase letters, numbers, and symbols) to ensure strict security.

### User Authentication
The application handles user login and logout, maintaining session data to track logged-in users. It also provides functionality for users to change their passwords.

### Budget Management
Authenticated users can create new budget plans, view existing plans, and edit or delete plans as needed. Each budget plan contains details such as income, expenses, and savings goals.

## Future Improvements
Future enhancements to Budget Helper could include:
- **Marking Functionality**: Allow the user to mark bills as paid, or deposits as posted.
- **Enhanced Budget Analysis**: Providing detailed analysis and visualizations of budget data to help users understand their spending habits better.
- **Multi-User Support**: Allowing multiple users to collaborate on a single budget plan.
- **API Integration**: Integrating with financial APIs to automatically fetch and update budget data based on user transactions.
- **Containerization**: Containerize the app for easy deployment.

## Conclusion
Budget Helper is a comprehensive tool designed to assist users in managing their finances efficiently. With its focus on security, responsiveness, and user experience, it aims to be a valuable resource for individuals looking to gain better control over their financial planning.

Feel free to reach out with any questions or feedback on the project. Happy budgeting!
