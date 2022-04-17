import datetime

from mongoengine.fields import FloatField, StringField


class TimeStampField(FloatField):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

    def _convert_from_datetime(self, data):

        return data.timestamp()

    def _convert_from_timestamp(self, data):

        return datetime.datetime.fromtimestamp(data)

    def __get__(self, instance, owner):
        if instance is None:
            return self

        data = super().__get__(instance, owner)

        if isinstance(data, datetime.datetime) or data is None:
            return data
        return self._convert_from_timestamp(data)

    def __set__(self, instance, value):
        super().__set__(instance, value)
        value = instance._data[self.name]
        if value is not None:
            if isinstance(value, datetime.datetime):
                instance._data[self.name] = self._convert_from_datetime(value)
            else:
                instance._data[self.name] = value

    def validate(self, value):
        value = self.to_python(value)
        if not isinstance(value, datetime.datetime):
            self.error("Only datetime objects may used in a TimeStampField")

    def to_python(self, value):
        original_value = value
        try:
            return self._convert_from_timestamp(value)
        except Exception:
            return original_value

    def to_mongo(self, value):
        value = self.to_python(value)
        return self._convert_from_datetime(value)

    # def prepare_query_value(self, op, value):
    #     return super().prepare_query_value(op, self._convert_from_datetime(value))