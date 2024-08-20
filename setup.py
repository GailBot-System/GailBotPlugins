from setuptools import setup, find_packages

setup(
    name='GailBotPlugins',  
    version='0.1.0', 
    author='HiLab', 
    author_email='hil@elist.tufts.edu',  
    description='A set of tools for use in plugins',  
    long_description=open('README.md').read(),  
    long_description_content_type='text/markdown', 
    url='https://github.com/GailBot-System/GailBotPlugins',  
    packages=find_packages(),  
    include_package_data=True,  # Include additional files specified in MANIFEST.in
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # ??
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6', 
    install_requires=[
        'lxml',
        'gailbot',
        'pydantic',
    ],
)
