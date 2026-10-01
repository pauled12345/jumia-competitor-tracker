from setuptools import setup, find_packages

setup(
    name="jumia-competitor-tracker",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.30.6",
        "sqlalchemy>=2.0.35",
        "pydantic>=2.9.2",
        "scrapling>=0.2.98",
        "httpx>=0.27.2",
        "apscheduler>=3.10.4",
    ],
)
