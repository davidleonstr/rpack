from setuptools import setup, find_packages

setup(
    name='rpack',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'setuptools'
    ],
    description='Python Resource File Packer',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='David León',
    author_email='davidalfonsoleoncarmona@gmail.com',
    url='https://github.com/davidleonstr/rpack',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11.3',
    include_package_data=True,
)

# I use Python 3.13.1.