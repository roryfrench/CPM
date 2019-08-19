import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cpm-pkg-roryfrench",
    version="0.0.1",
    author="Rory French",
    author_email="rfrench@logikalprojects.com",
    description="A package for calculating a project critical path using the critical path method",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/roryfrench/CPM.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)