from setuptools import setup, find_packages
from pathlib import Path
import os

#p = Path("~/.local/share/BlueToolkit")
#p.mkdir(parents=True, exist_ok=True)
#filepath = "~/.local/share/BlueToolkit/conf.conf"
#with open(filepath, 'w') as f:
#    f.write("loation=" + Path(__file__).as_posix() + "\n")

setup(
    name='bluekit',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        # Add your dependencies here
    ],
    entry_points={
        'console_scripts': [
            'bluekit=bluekit.bluekit:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
