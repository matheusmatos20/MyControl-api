from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
senha = "1234"
hash_gerado = pwd_context.hash(senha)
print(hash_gerado)
