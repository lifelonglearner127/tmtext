from setuptools import setup, find_packages
import os

setup(
    name='project',
    version='1.0',
    packages=find_packages(),
    entry_points={'scrapy': ['settings = product_ranking.settings']},
    zip_safe=False,  # Because of Captcha Breaker.
    include_package_data=True,
    data_files=[(root, [os.path.join(root, f) for f in files])
         for root, _, files in os.walk('train_captchas_data')],
    install_requires=[
        "Scrapy>=0.22",
    ],
    extras_require={
        'Captcha Breaker': ["numpy"],
    }
)
