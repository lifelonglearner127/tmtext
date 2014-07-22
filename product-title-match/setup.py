from setuptools import setup, find_packages

setup(
    name='product-title-match',
    version='1.0',
    packages=find_packages(),
    entry_points={'scrapy': ['settings = product_title_match.settings']},
    zip_safe=False,  # Because of Captcha Breaker.
    include_package_data=True,
    install_requires=[
        "Scrapy>=0.22",
        "product-ranking",
    ],
)
