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
            "dana-check-build-exists=dana_client.check_build_exists:main",
            "dana-publish-new-build=dana_client.publish_new_build:main",
            "dana-publish-backup=dana_client.publish_backup:main",
        ],
    },
)
