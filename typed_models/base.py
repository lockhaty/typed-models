from .exceptions import DefaultNotProvided, UnassignedOptionalFieldRequested, InvalidFieldArguments

NOT_PROVIDED = object()


class Field:

    def __init__(self, default=NOT_PROVIDED, optional=False):

        if default is not NOT_PROVIDED and optional:
            raise InvalidFieldArguments(f"'{self.__class__.__name__}' cannot be both optional and have a default")

        self.default = default
        self.optional = optional
        self.field_name = 'Field'

    def get_default(self):

        if self.default is not NOT_PROVIDED:
            return self.default

        if self.optional:
            return NOT_PROVIDED

        raise DefaultNotProvided(f"Field '{self.field_name}' has no default specified and is not optional")

    def parse(self, value):
        return value

    def default_serializer(self, value):
        return str(value)

    @classmethod
    def is_field(cls, value):
        return isinstance(value, cls)

    def _raise_value_error(self, value):
        raise ValueError(
            f'Field "{self.field_name}" with value "{value}" could not be parsed as a {self.__class__.__name__}') from None


class FieldValue:

    def __init__(self, field: Field, value=NOT_PROVIDED):
        self.field = field
        self.value = value

    def get(self):
        if self.value is NOT_PROVIDED:
            self.value = self.field.get_default()

        if self.is_not_provided():
            raise UnassignedOptionalFieldRequested(
                f"Optional Field '{self.field.field_name}' was not assigned and was requested")

        return self.value

    def set(self, value):
        self.value = self.field.parse(value)

    def is_not_provided(self):
        return self.value is NOT_PROVIDED


class ModelMeta(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        module = attrs.pop('__module__')
        base_attrs = {'__module__': module}

        fields = {}

        for key, value in list(attrs.items()):
            if Field.is_field(value):
                fields[key] = value
                fields[key].field_name = key
            else:
                base_attrs[key] = value

        new_class = super().__new__(cls, name, bases, base_attrs, **kwargs) # noqa

        new_class._model_meta = {
            'fields': fields,
            'field_values': {}
        }
        return new_class


class Model(metaclass=ModelMeta):

    def __init__(self, dict_=None, **kwargs):
        if dict_ is None:
            dict_ = {}
        source = {**dict_, **kwargs}

        for field_name in self._model_meta['fields']:
            field: Field = self._model_meta['fields'][field_name]
            field_value = FieldValue(field=field)
            try:
                value = source.pop(field_name)
            except KeyError:
                value = field.get_default()

            field_value.set(value)

            self._model_meta['field_values'][field_name] = field_value

    def __getattribute__(self, item):
        if item in ['_model_meta']:
            return super().__getattribute__(item)

        if item not in self._model_meta['fields']:
            return super().__getattribute__(item)

        field_value: FieldValue = self._model_meta['field_values'][item]
        return field_value.get()

    def __setattr__(self, key, value):

        if key not in self._model_meta['fields']:
            super().__setattr__(key, value)
            return

        field_value: FieldValue = self._model_meta['field_values'][key]
        field_value.set(value)
