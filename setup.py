from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="py-context-llm7",
    version="0.1.0",
    author="Eugene Evstafev",
    author_email="support@llm7.io",
    description="Minimal Python client for https://api.context.llm7.io",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chigwell/py-context-llm7",
    project_urls={
        "Source": "https://github.com/chigwell/py-context-llm7",
        "Issues": "https://github.com/chigwell/py-context-llm7/issues",
    },
    packages=find_packages(exclude=("tests", "tests.*")),
    install_requires=["requests>=2.28,<3"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.8",
    license="MIT",
    keywords=["llm", "client", "context", "vector", "rag"],
    tests_require=["unittest"],
    test_suite="tests",
    include_package_data=True,
    zip_safe=False,
)
