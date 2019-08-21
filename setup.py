import setuptools
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name="cpm_calculator",
    version="0.0.1",
    author="Rory French",
    author_email="rfrench@logikalprojects.com",
    description="A package for calculating a project critical path using the critical path method",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/roryfrench/CPM.git",
    # py_modules=["cpm.py"],
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords='criticalpath',
    python_requires='>=3',
    install_requires=['datetime', 'workdays'],  # Optional
     project_urls={  # Optional
        'Source': 'https://github.com/roryfrench/CPM',
    },
)