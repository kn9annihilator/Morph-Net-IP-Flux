# setup.py
from setuptools import setup, find_packages

# Read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="morphnet-ip-flux",
    version="1.0.0",
    author="Krishna Narula",
    description="A Moving Target Defense framework for proactive cyber deception.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        "PyYAML",
        "python-dotenv",
        "requests",
        "cryptography",
        "rich",
    ],
    entry_points={
        'console_scripts': [
            'morphnet-engine=main:main',
            'morphnet-dashboard=dashboard:run_dashboard',
        ],
    },
    python_requires='>=3.7',
)