from setuptools import setup, find_packages

setup(
    name="skin-cancer-detector",
    version="0.1.0",
    description="Skin cancer classification using deep learning — thesis project",
    author="Hung Dang",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "torch>=2.2.0",
        "torchvision>=0.17.0",
        "timm>=0.9.16",
        "albumentations>=1.4.0",
        "hydra-core>=1.3.2",
        "omegaconf>=2.3.0",
        "numpy>=1.26.0",
        "pandas>=2.2.0",
        "scikit-learn>=1.4.0",
        "tqdm>=4.66.0",
    ],
)
