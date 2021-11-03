import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

ms_recommend_extras = ['tensorflow==2.2.0', 'keras', 'torch', 'cornac', 'recommenders']

setuptools.setup(
    name="librec-auto",
    version="0.2.6",
	scripts=['librec_auto/__main__.py'] ,
    author="Masoud Mansoury, Nasim Sonboli, Robin Burke, Will Mardick-Kanter and others",
    author_email="masoodmansoury@gmail.com",
    description=
    "The librec-auto project aims to automate recommender system experiments using LibRec.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/that-recsys-lab/librec-auto",
    packages=setuptools.find_packages(),
	include_package_data=True,
	install_requires=['matplotlib',
                      'pandas',
                      'numpy',
                      'progressbar',
                      'lxml',
                      'cryptography',
                      'slackclient>=2.0',
                      'slack',
                      'slacker',
                      'optuna',

    ],
    extras_require={ 'ms_recommend': ms_recommend_extras },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
