from setuptools import setup, find_packages

setup(
    name="openimis-be-notification",
    version="1.0.0",
    description="Notification module for openIMIS — in-app, email, SMS delivery",
    license="AGPL-3.0-only",
    packages=find_packages(),
    install_requires=[
        "django",
        "djangorestframework",
        "openimis-be-core",
    ],
    package_data={
        "notification": ["templates/**/*"],
    },
)
