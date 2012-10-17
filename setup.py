from setuptools import setup, find_packages

description="""
PostgreSQL native geometric types and fields  extension for Django.
"""

setup(
    name = "djorm-ext-pggeom",
    version = '0.4.1',
    url = 'https://github.com/niwibe/djorm-ext-pggeom',
    license = 'BSD',
    platforms = ['OS Independent'],
    description = description.strip(),
    author = 'Andrey Antukh',
    author_email = 'niwi@niwi.be',
    maintainer = 'Andrey Antukh',
    maintainer_email = 'niwi@niwi.be',
    install_requires = [
        'djorm-ext-core >= 0.4',
    ],
    packages = ['djorm_pggeom'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
