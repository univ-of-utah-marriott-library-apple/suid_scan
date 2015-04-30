from distutils.core import setup
import suid_scan

setup(
    name='SUID Scan',
    version=suid_scan.__version__,
    url='https://github.com/univ-of-utah-marriott-library-apple/suid_scan',
    author='Pierce Darragh, Marriott Library IT Services',
    author_email='mlib-its-mac-github@lists.utah.edu',
    description='Simple script to help you check for files with execute-as bits set.',
    license='MIT',
    scripts=['suid_scan.py'],
    classifiers=[
        'Development Status :: 5 - Stable',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7'
    ],
)
