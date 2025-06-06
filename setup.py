from setuptools import setup, find_packages

setup(
    name="anthropic_api_file_tools",
    version="0.1",
    packages=find_packages(),
    py_modules=["anthropic_api_file_tools"],
    install_requires=[
        "anthropic"
    ],
)