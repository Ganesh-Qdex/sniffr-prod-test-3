from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId
from models.auth import UserRole


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    age: Optional[int] = Field(None, ge=0, le=150)
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    address: Optional[str] = Field(None, max_length=500)
    is_active: bool = True
    role: UserRole = UserRole.USER
    last_login: Optional[datetime] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=0, le=150)
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    address: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


class User(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "age": 30,
                "phone": "+1234567890",
                "address": "123 Main St, City, State",
                "is_active": True
            }
        }


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    age: Optional[int]
    phone: Optional[str]
    address: Optional[str]
    is_active: bool
    role: UserRole
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {ObjectId: str}
