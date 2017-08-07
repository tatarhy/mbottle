from setuptools import setup

setup(
    name='mbottle',
    packages=['mbottle'],
    include_package_data=True,
    install_requires=[
        'flask',
        'Flask-OAuthlib',
    ],
)
