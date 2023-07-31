from setuptools import setup, find_packages


setup(
    name="fastapi-sa-manager",
    version="0.1.2",
    description="FastAPI-sa-manager is an SQLAlchemy ORM extension for FastAPI helping you to build CRUD APIs fast and easy.",
    author="esanzy87",
    author_email="esanzy87@gmail.com",
    install_requires=["fastapi", "sqlalchemy"],
    packages=find_packages(exclude=[]),
    keywords=["fastapi", "sqlalchemy"],
    python_requires=">=3.10",
    package_data={},
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
