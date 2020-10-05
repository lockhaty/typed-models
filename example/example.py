import enum
import json
​
from typed_models import Model
from typed_models.fields import StringField, DateTimeField, DecimalField, EnumField, ModelField, BooleanField, \
    IntegerField, FloatField, ListField
​
​
class EmployeeType(enum.Enum):
    ADMIN = 'admin'
    DEVELOPER = 'developer'
​
class Employee(Model):
​
    employee_name = StringField()
    employee_number = IntegerField()
    is_active = BooleanField(default=True)
    nick_name = StringField(optional=True)
    employee_type = EnumField(enum_type=EmployeeType, default=EmployeeType.DEVELOPER)
​
class Company(Model):
​
    company_id = StringField()
    company_name = StringField()
    employees = ListField(list_type=ModelField(model_class=Employee))
​
    created_at = DateTimeField(tz='Africa/Johannesburg', default=DateTimeField.AUTO_NOW)
​
​
​
if __name__ == '__main__':
​
    company = Company(company_id='1', company_name='A2D24')
​
    company.employees.append(Employee(
        {
            "employee_name": "Imtiaz",
            "employee_number": 1,
        }
    ))
    company.employees.append(Employee(employee_name="Dennis", employee_number=2, nick_name="DC"))
    company.employees.append(dict(employee_name='Yusuff', employee_number=3))
    company.employees.append({"employee_name": "Suhail", "employee_number": "4"})
​
    print(company.created_at)
​
    company.created_at = '2020-01-01T00:00:00Z'
    print(company.created_at)
    print(type(company.created_at))
​
    try:
        company.created_at = 'invalid date'
    except ValueError as e:
        print(e)
​
    print(json.dumps(company.serialize(), indent=4))
