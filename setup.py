from setuptools import setup, find_packages

version = "1.0.0"

setup(
    name="jaw-tracking-system",
    version=version,
    description="Modular and flexible jaw motion analysis framework (motion capture, calibration, registration, "
                "and analysis)",
    long_description="""
        JawTrackingSystem (JTS): Modular and flexible jaw motion analysis framework.
        This package provides an abstract framework for analyzing motion capture data, with specific implementations 
        for jaw motion analysis. The design allows for easy extension to other motion capture systems beyond Qualisys.
    """,
    long_description_content_type="text/markdown",
    author="Paul-Otto Müller",
    author_email="pmueller@sim.tu-darmstadt.de",
    url="https://github.com/paulotto/jaw_tracking_system",
    license="CC BY-NC-SA 4.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "h5py",
        "numpy",
        "scipy",
        "pandas",
        "scikit-learn",
        "matplotlib"
    ],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Medical Science Apps",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    keywords="motion-capture jaw-analysis jaw-tracking biomechanics calibration registration",
    entry_points={
        "console_scripts": [
            "jts-analysis = jts.core:main",
        ],
    },
    package_data={
        # Include config files, if needed
        "jaw_tracking_system": ["config/config.json", "config/README.md", "README.md"],
    },
    project_urls={
        "Source": "https://github.com/paulotto/jaw_tracking_system",
        "Bug Tracker": "https://github.com/paulotto/jaw_tracking_system/issues",
        "License": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
    },
)
