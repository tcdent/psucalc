from distutils.core import setup

setup(
    name='psucalc',
    version='0.1',
    description='Power supply hierarchy and current modeler',
    author="a10k, Inc.", 
    author_email="root@a10k.co", 
    packages=('psucalc', ), 
    entry_points={
        'console_scripts': [
            'psucalc = psucalc.__main__:main'
        ]
    })

