from ast import For
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, selectinload
from helper import Base

engine = create_engine('sqlite:///data.db', echo=True)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

class Company(Base):
    __tablename__ = 'company'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    employees = relationship("Employee", back_populates="company")

class Employee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    type = Column(String(50))
    company_id = Column(ForeignKey('company.id'))
    company = relationship("Company", back_populates="employees")

    __mapper_args__ = {
        'polymorphic_identity':'employee',
        'polymorphic_on':type
    }

class Engineer(Employee):
    __tablename__ = 'engineer'
    id = Column(Integer, ForeignKey('employee.id'), primary_key=True)
    engineer_info = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity':'engineer',
    }

class Manager(Employee):
    __tablename__ = 'manager'
    id = Column(Integer, ForeignKey('employee.id'), primary_key=True)
    manager_data = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity':'manager',
    }


with engine.connect() as con:
    con.execute("drop table if exists manager;")
    con.execute("drop table if exists engineer;")
    con.execute("drop table if exists employee;")
    con.execute("drop table if exists company;")
print(repr(Base.metadata.create_all(engine)))

company = Company(name="company1")
engineer = Engineer(name="engineer1", engineer_info="engineer_info1")
manager = Manager(name="manager1", manager_data="manager_data1")
company.employees = [engineer, manager]
session.add_all([company, engineer, manager])
session.flush()
session.commit()

"""
SELECT company.id AS company_id, company.name AS company_name 
FROM company
SELECT employee.id AS employee_id, employee.name AS employee_name, employee.type AS employee_type, employee.company_id AS employee_company_id 
FROM employee 
WHERE ? = employee.company_id
"""
company = session.query(Company).one() 
print(company.employees) # select from company then select from employee where company.id = ?

"""
SELECT employee.id AS employee_id, employee.name AS employee_name, employee.type AS employee_type, employee.company_id AS employee_company_id 
FROM employee
"""
employees = session.query(Employee).all() # select from employee table
print(employees)

"""
SELECT engineer.id AS engineer_id, employee.id AS employee_id, employee.name AS employee_name, employee.type AS employee_type, employee.company_id AS employee_company_id, engineer.engineer_info AS engineer_engineer_info 
FROM employee JOIN engineer ON employee.id = engineer.id
"""
engineers = session.query(Engineer).all() # select from join engineer and employee table
print(engineers)