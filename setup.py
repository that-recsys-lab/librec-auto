import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="librec-auto",
    version="0.0.16",
	scripts=['librec_auto\__init__.py'] ,
    author="Masoud Mansoury and Robin Burke",
    author_email="masoodmansoury@gmail.com",
    description="The librec-auto project aims to automate recommender system experimens using Librec.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/that-recsys-lab/librec-auto",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
