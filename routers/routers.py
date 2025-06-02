from bson import ObjectId
from fastapi import FastAPI, APIRouter, BackgroundTasks, HTTPException, Depends

from database import collection
from schemas.schemas import all_task, individual_data
from utils.security import verify_password, get_current_user, create_access_token, pwd_context
from utils.utils import send_confirmation_email
from models.models import Task
from fastapi.security import OAuth2PasswordRequestForm
from models.models import UserRegister

app = FastAPI()
router = APIRouter()


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = collection.find_one({"username": form_data.username})

    if not db_user:
        raise HTTPException(status_code=404, detail="Incorrect username or password")

    hashed_pw = db_user.get("hashed_password")
    if not hashed_pw or not verify_password(form_data.password, hashed_pw):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token = create_access_token({"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/")
async def get_all_tasks(current_user: str = Depends(get_current_user)):
    try:
        data = collection.find()
        return all_task(data)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/register", status_code=201)
def register(user: UserRegister):
    # Check if user already exists
    if collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already registered")

    # Hash the password
    hashed_password = pwd_context.hash(user.password)

    # Save user with hashed password to MongoDB
    user_dict = {"username": user.username, "hashed_password": hashed_password}
    collection.insert_one(user_dict)

    return {"status_code": 201, "msg": "User registered successfully"}


@router.get("/")
async def get_all_tasks(current_user: str = Depends(get_current_user)):
    data = collection.find()
    return all_task(data)


@router.post("/create", status_code=201)
async def create_task(
        new_task: Task,
        background_tasks: BackgroundTasks,
        current_user: str = Depends(get_current_user)
    ):
    try:
        resp = collection.insert_one(new_task.dict())
        background_tasks.add_task(send_confirmation_email, new_task.title, new_task.email)
        return {"status_code": 200, "id": str(resp.inserted_id)}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Some error occurred: {e}")


@router.get("/{task_id}")
async def get_task(task_id: str, current_user: str = Depends(get_current_user)):
    try:
        id = ObjectId(task_id)  # Convert string to ObjectId
        data = collection.find_one({"_id": id})
        if not data:
            raise HTTPException(status_code=404, detail="Task does not exist")

        # Use your existing individual_data() helper to format the task
        return individual_data(data)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Some error occurred: {e}")


@router.put("/{task_id}")
async def update_task(task_id: str, updated_task: Task, current_user: str = Depends(get_current_user)):
    try:
        id = ObjectId(task_id)
        task = collection.find_one({"_id": id})
        if not task:
            raise HTTPException(status_code=404, detail="Task does not exist")

        resp = collection.update_one({"_id": id}, {"$set": updated_task.dict()})
        return {"status_code": 200, "message": "Task Updated Successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Some error occurred: {e}")


@router.delete("/{task_id}")
async def delete_task(task_id: str, current_user: str = Depends(get_current_user)):
    try:
        id = ObjectId(task_id)
        existing_task = collection.find_one({"_id": id})
        if not existing_task:
            raise HTTPException(status_code=404, detail="Task does not exist")

        resp = collection.delete_one({"_id": id})
        return {"status_code": 200, "message": "Task Deleted Successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Some error occurred: {e}")


app.include_router(router)
