import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="libxduauth",
    version="1.8.2",
    author="Frank",
    author_email="frankli0324@hotmail.com",
    description="Login utilities for XDU",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xdlinux/libxduauth",
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
