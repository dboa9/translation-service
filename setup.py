from setuptools import setup, find_packages

setup(
    name="translation_service",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "torch",
        "transformers",
        "streamlit",
        "requests",
        "pyyaml"
    ],
    python_requires=">=3.8",
)