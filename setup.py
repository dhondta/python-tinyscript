from distutils.core import setup


setup(
  name = "tinyscript",
  packages = ["tinyscript"],
  version = "0.1",
  license = "GPLv3",
  description = "A tiny library for easily building \"self-contained\" CLI "
                "Python tools with base features in a shortened way",
  author = "Alexandre D\'Hondt",
  author_email = "alexandre.dhondt@gmail.com",
  url = "https://github.com/dhondta/tinyscript",
  download_url = "https://github.com/dhondta/tinyscript/archive/0.1.tar.gz",
  keywords = ["CLI tool", "logging"],
  classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
  ],
  python_requires = '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4',
)
