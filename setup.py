from pathlib import Path
from setuptools import setup, find_packages

metadata_path = Path(__file__).parent / 'src' / 'xarray_events' / '__about__.py'
metadata = {}
with metadata_path.open() as file:
    raw_code = file.read()
exec(raw_code, metadata)
metadata = {key.strip('_'): value for key, value in metadata.items()}
metadata['name'] = metadata.pop('package_name')

setup(
    long_description=open('docs/README.rst').read(),

    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[path.stem for path in Path('src').glob('*.py')],
    zip_safe=True,

    install_requires=[
        'xarray',
        'pytest-mypy',
        'pytest-flake8',
        'pytest-pydocstyle',
        'pytest-coverage'
    ],
    extras_require=dict(
        dev=[
        ],
    ),

    **metadata,
)
