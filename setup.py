import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="libxduauth",
    version="1.4.3",
    author="Frank",
    author_email="frankli0324@hotmail.com",
    description="login utilities for XDU",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/frankli0324/libxdauth",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.5',
    install_requires=[
        "requests", "Pillow", "bs4",
        "pytesseract", "importlib-resources"
    ],
    package_data={
        "libxduauth": ["*.traineddata"],
    },
)
