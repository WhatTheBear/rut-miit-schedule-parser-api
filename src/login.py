from hashlib import sha256
from src.journal import Journal


class Login:

    def __init__(self, jr: Journal):
        self.jr = jr

    def _hash_password(self, password: str) -> str:

        encoded_password_string = password.encode('utf-8')

        obj_sha256 = sha256(encoded_password_string)

        return obj_sha256.hexdigest()
    
    def _generate_auth_token(self) -> str:
        pass


    def register(self, userName: str, login: str, password: str) -> str:
 
        if self.jr.getUserByLogin(login) is not None: 
            return "Пользователь с таким логином уже существует."
        
        hashed_password = self._hash_password(password)

        loginData: dict = {
            "userName": userName,
            "login": login,
            "password": hashed_password
        }

        self.jr.createUser(loginData)

        return "401"









        






        

    