try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='django-cdn-finder',
    version='0.1dev',
    author='bung',
    packages=[
        'cdn_finder',
        'cdn_finder/templatetags'
    ],
    install_requires=['Django'],
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)