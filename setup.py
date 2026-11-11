from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="webclone",
    version="2.0.0",
    author="WebClone Team",
    description="Yüksek hızlı, anonim ve istihbarat destekli modern web sitesi kopyalama aracı.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/webclone",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Utilities",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.28.0",
        "urllib3>=1.26.0",
        "PyQt6>=6.4.0",
        "PySocks>=1.7.1",
    ],
    extras_require={
        "browser": ["PyQt6-WebEngine>=6.4.0"],
    },
    entry_points={
        "console_scripts": [
            "webclone=webclone.cli:main",
            "webclone-gui=webclone.gui:launch_gui",
        ],
    },
    package_data={
        "webclone": ["*.svg", "*.png"],
    },
)
