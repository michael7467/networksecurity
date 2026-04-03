
''' 
The setup.py is an essential part of packaging and distributing Python projects.
It is used by Setuptools to define the configuration of a project such as its metadata dependency,
 and more
 '''

from setuptools import setup, find_packages
from typing import List

def get_requirements() -> List[str]:
    ''' 
    Reads the requirements from a file and returns them as a list of strings.
    '''
    requirement_list: List[str] = []
    try:
            with open('requirements.txt', 'r') as file:
                #Read lines from the file and split them into a list of strings
                lines = file.readlines()
                for line in lines:
                    #Strip whitespace and newline characters from each line
                    requirement = line.strip()
                    #Ignore empty lines and comments
                    if requirement and requirement!='-e .':
                        requirement_list.append(requirement)
 
      
    except FileNotFoundError:
        print("requirements.txt file not found.")
       

    return requirement_list

setup(
    name='NetworkSecurity',
    version='0.1.0',
    description='A Python package for network security analysis and tools.',
    author='Michael Mogos',
    author_email='michaelmogos746@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements(),    
    classifiers=[
        'Development Status <IP_ADDRESS> 3 - Alpha',
        'Intended Audience <IP_ADDRESS> Developers',
        'Programming Language <IP_ADDRESS> Python <IP_ADDRESS> 3',
        'Programming Language <IP_ADDRESS> Python <IP_ADDRESS> 3.8',
    ],
)
