#!/usr/bin/env python3
"""
Setup configuration for BYOD Compliance Monitor.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="byod-compliance-monitor",
    version="1.0.0",
    author="Security Professional",
    description="Enterprise-grade BYOD compliance monitoring for Android devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/byod-compliance-monitor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    py_modules=["main"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        # No external dependencies required for core functionality
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'black>=23.0.0',
            'pylint>=2.17.0',
        ],
        'reports': [
            'jinja2>=3.1.2',
        ],
        'encryption': [
            'cryptography>=41.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'byod-monitor=main:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
