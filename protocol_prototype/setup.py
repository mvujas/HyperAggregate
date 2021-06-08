from setuptools import setup

with open('requirements.txt', 'r') as f:
    required_packages = f.read().splitlines()

setup(
    name='hyperaggregate',
    version="0.0.1",
    author="Milos Vujasinovic",
    author_email="milos.vujasinovic@epfl.ch",
    description="A sublinear secure aggregation algorithm implementation",
    url="https://github.com/epfml/semester-project-milos",
    project_urls={
        "Bug Tracker": "https://github.com/epfml/semester-project-milos/issues",
    },
    install_requires=required_packages,
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6"
)
