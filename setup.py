import os

from setuptools import find_packages, setup

# Update manually
VERSION = "0.1.0dev"


def get_requirements():
    return []


def main():

    version_file = os.path.join(
        os.path.dirname(__file__), "knodia", "_version.py"
    )
    with open(version_file, "w") as f:
        f.write(f"version = \"{VERSION}\"\n")

    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

    setup(
        name="knodia",
        license="MIT",
        version=VERSION,
        packages=find_packages(include=["knodia"]),
        author="Nicola De Mitri",
        author_email="nicola.dmt@gmail.com",
        description="Tools for knot diagrams",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/nicolasap-dm/knodia",
        project_urls={
            "Bug Tracker": "https://github.com/nicolasap-dm/knodia/issues",
        },
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        python_requires=">=3.6",
        install_requires=get_requirements()
    )


if __name__ == "__main__":
    main()
