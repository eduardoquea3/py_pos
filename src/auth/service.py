from config.database import DatabaseEngine
from src.auth.model import UserModel


def find_user(username: str) -> UserModel:
    engine = DatabaseEngine()
    engine.create_engine()

    result = engine.execute_procedure("find_by_username", (username,))

    if result and len(result) > 0:
        user_data = result[0]
        print(f"User found: {user_data}")
        user = UserModel(
            id=user_data["id"],
            username=user_data["username"],
            password=user_data["password"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
        )
        return user
    return None
