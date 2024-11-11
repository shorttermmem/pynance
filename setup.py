from setuptools import setup, find_packages

setup(
    name="pynance",
    version="0.1.0",
    description="OpenGL Graphics Engine in Python (Pygame, ModernGL)",
    author="stm",
    author_email="noreply@example.com",
    url="https://github.com/shorttermmem/pynance",  # Update with the actual URL
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    install_requires=[
        "moderngl",
        "numpy",
        "pygame",
        "PyGLM",
        "pywavefront",
        "memory_profiler"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Update the license if needed
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.12',  # Specify the python version if needed
)
