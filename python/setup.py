from setuptools import setup, find_packages

setup(
    name="mydre-upload-sdk",
    version="1.0.0",
    description="Python client library for myDRE Workspace uploads",
    author="anDREa Team",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "azure-storage-blob>=12.0.0",
        "pandas>=1.0.0",
    ],
    python_requires=">=3.8",
)
