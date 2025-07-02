from setuptools import setup, find_packages

setup(
    name='pyminiping',
    version='0.3.0',
    description='Pure Python ICMP ping with statistics and hop count',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Pavel Loginov',
    author_email='aidaho@roxy-wi.org',
    url='https://github.com/roxy-wi/pyminiping',
    packages=find_packages(),
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: System :: Networking :: Monitoring',
    ],
    license='MIT',
    include_package_data=True,
)
