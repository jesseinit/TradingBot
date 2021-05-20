from main import db


class UtilityMixin:
    def save(self):
        """Function for saving new objects"""
        db.session.add(self)
        db.session.commit()
        return self

    def update(self, **kwargs):
        """Function for updating objects"""
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self.save()
