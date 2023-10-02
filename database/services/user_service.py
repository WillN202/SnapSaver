from werkzeug.security import generate_password_hash, check_password_hash
from ..repositories.user_database_repository import UserDatabseRepository
from ..repositories.user_shib_repository import UserShibRepository
from ..models.user import User


class UserService:
    """Service responsible for coordinating user data inside the database or the University Shib login system"""

    def __init__(self):
        self.database_repository = UserDatabseRepository()
        self.shib_repository = UserShibRepository()

    def verify(self, email: str, password: str):
        """Verify a user exists and their credentials match stored records in the database or in Shib.

        Args:
            email (str): The email address of the logging in user.
            password (str): The password of the logging in user.

        Returns:
            result (boolean): True if the user exists and the credentials match, false otherwise.
        """

        login_methods = [self.database_repository, self.shib_repository]

        for method in login_methods:
            user = method.find_by_email(email)

            if not user:
                continue

            if check_password_hash(user.password, password):
                return True

        return False

    def find_by_email(self, email: str):
        """Finds a user by their email from the database only.

        Parameters:
            user_id (str): The email for the queried user.

        Returns:
            result (User): The user object matching that email. None if a user with that email does not exist.
        """

        return self.database_repository.find_by_email(email)

    def find_by_id(self, id: str):
        """Finds a user by their user ID from shib or the database

        Parameters:
            user_id (str): The user ID for the queried user.

        Returns:
            result (User): The user object matching that id. None if a user with that id does not exist.
        """
        result = self.database_repository.find_by_id(id)

        return result if result else self.shib_repository.find_by_id(id)

    def insert(self, user: User):
        """Insert a new user to the database.

        Parameters:
            user (User): User to be inserted with an unhashed & unsalted password.

        Returns:
            result (boolean): True if the operation is susccessful, false if the operation is unsuccessful.
        """

        if self.find_by_email(user.email):
            return False

        user.password = generate_password_hash(user.password)

        return self.database_repository.add(user)

