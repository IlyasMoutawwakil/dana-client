from setuptools import find_packages, setup


INSTALL_REQUIRES = [
    "huggingface_hub",
    "GitPython",
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
            "publish-backup=dana_client.publish_backup:main",
            "update-project=dana_client.update_project:main",
        ],
    },
)
