from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base, engine, SessionLocal

# Association table for mentorship matching
mentorship = Table(
    'mentorship', Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id')),
    Column('alumni_id', Integer, ForeignKey('alumni.id'))
)

class Student(Base):
    _tablename_ = 'students'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    skills = Column(String)
    mentors = relationship("Alumni", secondary=mentorship, back_populates="mentees")

class Alumni(Base):
    _tablename_ = 'alumni'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    skills = Column(String)
    mentees = relationship("Student", secondary=mentorship, back_populates="mentors")

# create all tables
Base.metadata.create_all(bind=engine)

# pre-populate data
students_data = [
    {"name": f"Student{i+1}", "email": f"student{i+1}@example.com", "password": "pass123", "skills": "Python,SQL"}
    for i in range(10)
]

alumni_data = [
    {"name": f"Alumni{i+1}", "email": f"alumni{i+1}@example.com", "password": "pass123", "skills": "Python,Java"}
    for i in range(10)
]

db = SessionLocal()
try:
    for s in students_data:
        db.add(Student(**s))
    for a in alumni_data:
        db.add(Alumni(**a))
    db.commit()
finally:
    db.close()

print("Database initialised with 10 students and 10 alumni ✅")