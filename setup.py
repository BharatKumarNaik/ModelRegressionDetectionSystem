'''
setup.py file is an essential part of packaging and distributing Python projects. \
It is used by setuptools (or distutils in older python versions)
to define the configuration of your project, such as metadata,dependencies, and more.
'''

from setuptools import setup, find_packages
# find_pacakges will help in pacakging all the folder which have __init__
# we also have a find_namespace_pacakges it is to automatically make files available based on the folder structure.

def get_requirements():
    '''
    This will return list of requirements
    '''
    req_lst=[]
    try:
        with open('requirements.txt','r') as file:
            lines = file.readlines()
            for line in lines:
                requirement=line.strip()
                # Ignore -e .
                if requirement and requirement!='-e .':
                    req_lst.append(requirement)
    except FileNotFoundError:
        print("requirements.txt file is not found!")

setup(
    name="ModelRegressionDetectionSystem",
    version="0.0.1",
    author="Bharat Naik",
    author_email="bharathegde2002@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements()
)