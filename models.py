from sqlalchemy import Integer, String, Column, BigInteger, ForeignKey
from sqlalchemy.orm import Session, DeclarativeBase, relationship

import datetime

from config import engine


class BaseModel(DeclarativeBase):
    pass


class Users(BaseModel):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, unique=True)
    id_tg = Column(Integer, unique=True)
    first_name = Column(String(50))
    last_name = Column(String(50))


class Objects(BaseModel):
    __tablename__ = 'objects'

    id = Column(Integer, primary_key=True, index=True, unique=True)
    name = Column(String(150))
    date = Column(String(50))
    time_start = Column(BigInteger)
    time_end = Column(BigInteger)
    user_object = relationship('UsersObjects', back_populates='object')


class UsersObjects(BaseModel):
    __tablename__ = 'users_objects'

    id = Column(Integer, primary_key=True, index=True, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('Users')
    object_id = Column(Integer, ForeignKey('objects.id'))
    object = relationship('Objects', back_populates='user_object')
    is_active = Column(String)


async def set_models_id(user_id):
    with Session(bind=engine) as db:
        try:
            if not (db.query(Users).filter(Users.id_tg == user_id).first()):
                from_user_id = Users(id_tg=user_id)
                db.add(from_user_id)
                db.commit()
        except:
            db.rollback()


async def set_models_name(name, user_id):
    with Session(bind=engine) as db:
        try:
            student = db.query(Users).filter(Users.id_tg == user_id).first()
            student.first_name = name
            db.commit()
        except:
            db.rollback()


async def set_models_surname(surname, user_id):
    with Session(bind=engine) as db:
        try:
            student = db.query(Users).filter(Users.id_tg == user_id).first()
            student.last_name = surname
            db.commit()
        except:
            db.rollback()


async def set_models_plus(user_id, plus):
    with Session(bind=engine) as db:
        try:
            student = db.query(Users).filter(Users.id_tg == user_id).first()
            object_plus = db.query(Objects).filter(
                Objects.date == str(datetime.datetime.now().date()),
                Objects.time_start <= int(datetime.datetime.now().time().hour) * 60 + int(
                    datetime.datetime.now().time().minute), int(datetime.datetime.now().time().hour) * 60 + int(
                    datetime.datetime.now().time().minute) <= Objects.time_end
            ).first()
            if object_plus is None:
                return 'Сейчас нельзя отметиться'
            else:
                student_valid = db.query(UsersObjects).filter(UsersObjects.user_id == student.id,
                                                              UsersObjects.object_id == object_plus.id).first()
                if student_valid:
                    return 'Уже есть отметка'
                else:
                    message_plus = UsersObjects(user_id=student.id, object_id=object_plus.id, is_active=plus)
                    db.add(message_plus)
                    db.commit()
                    return f'Отметил на паре "{message_plus.object.name}" ✅'
        except:
            db.rollback()


async def select_models_fullname(user_id):
    with Session(bind=engine) as db:
        student = db.query(Users).filter(Users.id_tg == user_id).first()
        if student.first_name and student.last_name:
            return True
        return False


async def select_models_admin(message_date, objects_name):
    info = f'<b>{message_date}</b> 🕐\n'
    with Session(bind=engine) as db:
        list_users = db.query(UsersObjects).join(Objects, UsersObjects.object_id == Objects.id).filter(
            Objects.date == message_date).all()
        if len(list_users) != 0:
            for object_name in objects_name:
                info += f'\n📌 <b>{object_name[0]}</b>:\n'
                for user_one in list_users:
                    if user_one.object.name == object_name[0]:
                        info += f'{user_one.user.first_name} ' + f'{user_one.user.last_name}\n'
        else:
            info += 'Список пуст'
    return info
