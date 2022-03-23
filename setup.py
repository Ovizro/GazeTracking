import warnings
from setuptools import setup

try:
    with open("README.md", encoding='utf-8') as f:
        ldescription = f.read()
except OSError:
    warnings.warn("Miss file 'README.md', using default description.", ResourceWarning)
    ldescription = "This is a Python (2 and 3) library that provides a webcam-based eye tracking system. It gives you the exact position of the pupils and the gaze direction, in real time."

setup(
    name="gaze_tracking",
    version="1.0.0-Alpha",
    description="Eye Tracking library easily implementable to your projects",
    long_description=ldescription,

    author="antoinelame",
    maintainer="Ovizro",
    maintainer_email="Ovizro@hypercol.com",
    url="https://github.com/Ovizro/GazeTracking",

    packages=["gaze_tracking"],
    package_data={'':["*.dat"]},
    install_requires=["numpy", "opencv-python", "dlib"],

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)