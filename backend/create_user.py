###### CODE RUN IN KERNEL TO GET HASH to register a user ########

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
print(pwd_context.hash("password123"))

# OUTPUT: $2b$12$jO.ICVxcdxfe0rqrGtDxce0N84qvArYFomiIiHJlKCWv7Kmpj2eKq

################################################################

# cd backend
# run python -m app.models.new_user

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User

db: Session = next(get_db())  # get session

new_user = User(
    username="vincent",
    # password = "password123"
    hashed_password="$2b$12$jO.ICVxcdxfe0rqrGtDxce0N84qvArYFomiIiHJlKCWv7Kmpj2eKq",
    projects=["A100", "B200"]
)

db.add(new_user)
db.commit()
db.refresh(new_user)
print("User inserted:", new_user.id)
