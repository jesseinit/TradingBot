from main import db
from sqlalchemy.exc import SQLAlchemyError


class UtilityMixin:
    def save(self):
        """Function for saving new objects"""
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except SQLAlchemyError:
            db.session.rollback()

    def update(self, **kwargs):
        """Function for updating objects"""
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self.save()
