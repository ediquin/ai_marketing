from setuptools import setup, find_packages

setup(
    name="ai_marketing",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # Core dependencies
        "pydantic>=2.0.0",
        "httpx>=0.24.0",
        "python-dotenv>=0.19.0",
        "loguru>=0.6.0",
        "python-dateutil>=2.8.2",
        
        # LLM providers
        "google-generativeai>=0.3.0",
        "groq>=0.3.0",
        "openai>=1.0.0",
        
        # Utils
        "tiktoken>=0.4.0",
        "tenacity>=8.2.0",
    ],
    python_requires=">=3.9",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI Marketing Strategist - Lightweight version with essential agents",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ai-marketing-strategist",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
