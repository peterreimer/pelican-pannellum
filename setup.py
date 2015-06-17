from setuptools import setup
import os

def _read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(name='pelican-pannellum',
      version='0.1',
      description='Pannellum Plugin for pelican',
      long_description=_read('Readme.rst'),
      py_modules=['pannellum'],
      author='Peter Reimer',
      author_email='peter@4pi.org',
      url='https://github.com/peterreimer/pelican-pannellum',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 2.7'
          ],
      keywords=['pelican', 'pannellum', 'panorama'],
      include_package_data = True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Pillow',
          'fourpi.pannellum'
          'pelican'
          # -*- Extra requirements: -*-
      ],
)
