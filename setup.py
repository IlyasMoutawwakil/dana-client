from setuptools import find_packages, setup


INSTALL_REQUIRES = [
    "huggingface_hub",
    "coloredlogs",
    "omegaconf",
    "pandas",
]

setup(
    name="dana-client",
    version="0.0.1",
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    entry_points={
        "console_scripts": [
            "check-build-exists=dana_client.check_build_exists:main",
            "publish-build=dana_client.publish_build:main",
            "publish-backup=dana_client.publish_backup:main",
        ],
    },
)
