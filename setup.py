import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="libxduauth",
    version="0.0.1.dev",
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
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["requests"],
)