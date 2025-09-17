# from passlib.context import CryptContext

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def get_password_hash(password: str) -> str:
#     return pwd_context.hash(password)

# # exemplo:

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# senha_plana = "Admin1"
# senha_hash = pwd_context.hash(senha_plana)
# print(senha_hash)


from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = "Admin"
hash_from_db = "$2b$12$e10AnRKuhdMnFArpJhXuGeoTMaOFOOBoDUPjqdKPNJcCWznoX2v2."

print(pwd_context.verify(password, hash_from_db))  # deve retornar True