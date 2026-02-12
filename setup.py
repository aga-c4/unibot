from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="agaunibot",
    version="0.1",
    include_package_data=True,
    python_requires='>=3.8',
    packages=find_packages(),
    setup_requires=['setuptools-git-versioning'],
    install_requires=requirements,
    author="Konstantin Khachaturian",
    author_email="aga-c4@yandex.ru",
    license="BSD License (2-Clause)",
    description="Telegram bot framework",
    homepage="https://github.com/aga-c4/agaunibot",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    platform="OS Independent",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: BSD License (2-Clause)",
        "Operating System :: OS Independent",
    ],
    version_config={
       "dirty_template": "{tag}",
    }
)