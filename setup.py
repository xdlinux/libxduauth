import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="libxduauth",
    version="1.7.5",
    author="Frank",
    author_email="frankli0324@hotmail.com",
    description="login utilities for XDU",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xdlinux/libxdauth",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.7',
    install_requires=[
        "requests", "bs4", "pycryptodome",
        "importlib-resources", "Pillow",
    ],
)
