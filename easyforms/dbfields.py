"""
Contains fields used to select database models
"""

import logging

from . import basicfields

__author__ = 'Yu Lee Paul (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)


class DbCodeSelectField(basicfields.SelectField):
    """
    A select field that loads the database model by code
    """
    def __init__(self, name, db_model, values=None, **kwargs):
        if values is None:
            # This will only work if the model has a name field
            values = db_model.query.order_by(db_model.name).all()
            self.valid_codes = None
        else:
            self.valid_codes = [v.code for v in values]

        super(DbCodeSelectField, self).__init__(name, values, **kwargs)

        # Save the database model so that we can query it later
        self.db_model = db_model

    def convert_value(self):
        if self.value:
            if self.valid_codes and self.value not in self.valid_codes:
                self.error = 'Invalid selection'
            else:
                loaded_value = self.db_model.query.filter(self.db_model.code == self.value).first()

                if loaded_value:
                    self.value = loaded_value
                else:
                    self.error = 'Invalid value: %s' % self.value
                    self.value = None


class DbIdSelectField(basicfields.SelectField):
    """
    A select field that loads the database model by code
    """
    def __init__(self, name, db_model, values=None, **kwargs):
        if values is None:
            # This will only work if the model has a name field
            values = db_model.query.order_by(db_model.name).all()
            self.valid_ids = None
        else:
            self.valid_ids = [v.id for v in values]

        super(DbIdSelectField, self).__init__(name, values, **kwargs)

        # Save the database model so that we can query it later
        self.db_model = db_model

    def convert_value(self):
        if self.value:
            int_value = None
            try:
                int_value = int(self.value)
            except ValueError:
                pass

            if int_value is None:
                self.error = 'Invalid'
                
            if not self.error and self.valid_ids and int_value not in self.valid_ids:
                self.error = 'Invalid selection'

            if not self.error:
                loaded_value = self.db_model.query.filter(self.db_model.id == self.value).first()

                if loaded_value:
                    self.value = loaded_value
                else:
                    self.error = 'Invalid value: %s' % self.value
                    self.value = None

