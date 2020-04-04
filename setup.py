from pathlib import Path
from setuptools import setup, find_packages
from subprocess import check_output

metadata_path = Path(__file__).parent / 'src' / 'xarray_events' / '__about__.py'
metadata = {}
with metadata_path.open() as file:
    raw_code = file.read()
exec(raw_code, metadata)
metadata = {key.strip('_'): value for key, value in metadata.items()}
metadata['name'] = metadata.pop('package_name')

long_description_path = Path(__file__).parent / 'docs' / 'README.rst'

setup(
    long_description=open(long_description_path).read(),

    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[path.stem for path in Path('src').glob('*.py')],
    zip_safe=True,
    include_package_data=True,

    install_requires=[
        'xarray',
        'pandas',
        'numpy',
    ],
    extras_require=dict(
        tests=[
            'pytest-mypy',
            'pytest-flake8',
            'pytest-pydocstyle',
            'pytest-coverage',
        ],
        docs=[
            'jupyter_sphinx',
        ]
    ),

    **metadata,
)
