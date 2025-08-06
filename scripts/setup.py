from setuptools import setup, find_packages

import os
from pathlib import Path

# Get the project root directory (parent of scripts)
project_root = Path(__file__).parent.parent

with open(project_root / "README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open(project_root / "requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-automation",
    version="0.1.0",
    author="Ramgopal Bhat",
    author_email="ramgopalbhat10@gmail.com",
    description="A modular, intelligent browser automation testing framework using browser-use with LLM integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ramgopalbhat10/ai-automation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "myst-parser>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-automation=ai_automation.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "config": ["*.yaml", "*.yml"],
        "test_suites": ["**/*.yaml", "**/*.yml"],
    },
    keywords=[
        "browser automation",
        "testing",
        "ai",
        "llm",
        "selenium",
        "playwright",
        "browser-use",
        "natural language",
        "yaml",
        "test automation",
    ],
    project_urls={
        "Bug Reports": "https://github.com/Ramgopalbhat10/ai-automation/issues",
        "Source": "https://github.com/Ramgopalbhat10/ai-automation",
        "Documentation": "https://github.com/Ramgopalbhat10/ai-automation#readme",
    },
)