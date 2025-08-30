from setuptools import setup, find_packages

# Читаем README для long_description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Читаем requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ads-aggregator",
    version="1.0.0",
    author="Python Backend Developer",
    author_email="developer@example.com",
    description="Система агрегации рекламных данных из Meta Ads и Google Ads",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/ads-aggregator",
    project_urls={
        "Bug Tracker": "https://github.com/your-username/ads-aggregator/issues",
        "Documentation": "https://github.com/your-username/ads-aggregator/wiki",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ads-aggregator=ads_aggregator.cli:main",
        ],
    },
    keywords=[
        "advertising", "ads", "meta", "facebook", "google", "adtech", "martech",
        "api", "aggregation", "campaigns", "creatives", "rotation", "marketing"
    ],
    include_package_data=True,
    zip_safe=False,
)
