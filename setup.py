from setuptools import setup


setup(
    version='0.0.1alpha',
    name='taiga',
    # long_description=long_description,
    # description=description,
    download_url='https://github.com/hellupline/taiga/tarball/0.0.1',
    url='https://github.com/hellupline/taiga',
    author_email='hellupline@gmail.com',
    author='Renan Traba',
    keywords=['flask', 'sqlalchemy', 'crud', 'admin', 'manager'],

    license='LGPL3',
    classifiers=[
        ('License :: OSI Approved :: '
         'GNU Lesser General Public License v3 or later (LGPLv3+)'),
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    packages=['taiga', 'taiga.ext'],
    install_requires=[
        'cached-property',
        'werkzeug',
    ],
    extras_require={
        'test': ['nose', 'coverage'],
        'dev': ['ipython'],
    },
    zip_safe=False,
    include_package_data=True,
)
