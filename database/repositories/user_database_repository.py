from .database_repository_base import BaseDatabaseRepository
from ..models.user import User
from uuid import uuid4


class UserDatabseRepository(BaseDatabaseRepository):
    def add(self, user):
        """Create a new user in the database.

        Parameters:
            user (User): The user model object.

        Returns:
            result (boolean): True if the insert is successful, false if the operation is unsuccessful.
        """
        ID = str(uuid4())
        self.cursor.execute(
            "INSERT INTO user VALUES(%s, %s, %s, %s, %s)",
            [ID[0:6],
             user.email,
             user.password,
             user.name,
             user.postcode])
        self.db.commit()

        return True

    def find_by_email(self, email):
        """Finds a user by their email.

        Parameters:
            email (str): The email for the queried user.

        Returns:
            result (User): The user object matching that email. None if a user with that email does not exist.
        """

        self.cursor.execute(
            "SELECT * from user WHERE email=%s",
            [email])
        results = self.cursor.fetchall()

        if not results:
            return None

        results = results[0]
        return User(results[0], results[1], results[2], results[3], results[4])

    def find_by_id(self, user_id: str):
        """Finds a user by their user ID.

        Parameters:
            user_id (str): The user ID for the queried user.

        Returns:
            result (User): The user object matching that id. None if a user with that id does not exist.
        """

        self.cursor.execute(
            "SELECT * from user WHERE userID=%s",
            [user_id])
        results = self.cursor.fetchall()

        if not results:
            return None

        results = results[0]
        return User(results[0], results[1], results[2], results[3], results[4])

    def update_email(self, user):
        """Updates a users email.

        Paramters:
            user (User): the user to be updated.

        """

        self.cursor.execute("UPDATE user SET email=%s WHERE userID=%s", [user.email, user.userID])
        self.db.commit()

    def update_password(self, user):
        """Updates a users hashed and salted password.

        Paramters:
            user (User): the user to be updated.

        """

        self.cursor.execute("UPDATE user SET passwordhash=%s WHERE userID=%s", [user.password, user.userID])
        self.db.commit()

    def update_name(self, user):
        """Updates a users name.

        Paramters:
            user (User): the user to be updated.

        """

        self.cursor.execute("UPDATE user SET name=%s WHERE userID=%s", [user.name, user.userID])
        self.db.commit()

    def update_postcode(self, user):
        """Updates a users postcode.

        Paramters:
            user (User): the user to be updated.

        """
        self.cursor.execute("UPDATE user SET postcode=%s WHERE userID=%s", [user.postcode, user.userID])
        self.db.commit()
