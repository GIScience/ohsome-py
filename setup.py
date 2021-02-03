import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ohsome",
    version="0.9.0",
    author="Christina Ludwig",
    author_email="christina.ludwig@uni-heidelberg.de",
    description="Python client for the ohsome API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GIScience/ohsome-py",
    packages=["ohsome"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3",
)
