from setuptools import setup, find_packages

setup(
    name='rela',
    version='0.1.0',
    description='A tool for checking the correctness of network changes.',
    author='Xieyang Xu, Yifei Yuan',
    author_email='ashlippers@gmail.com, yifei.yuan@alibaba-inc.com',
    packages=find_packages(exclude=('tests')),
    install_requires=['tqdm', 'hfst', 'ipaddress', 'pytest'],
)