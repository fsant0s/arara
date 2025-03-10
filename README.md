# NEURON  
A framework for agent-based recommendation systems.  

## Run Locally  

Clone the project  

~~~bash  
  git clone https://github.com/fsant0s/neuron.git
~~~

Go to the project directory  

~~~bash  
  cd neuron
~~~

### Install dependencies

First, ensure you have Python 3.12 and the uv package manager installed.

To set up the development environment automatically:

~~~bash
./scripts/setup_dev_env.sh
~~~

This script will:
1. Create a virtual environment
2. Install all dependencies
3. Configure pre-commit hooks
4. Set up a basic test structure

Alternatively, install dependencies manually:

~~~bash  
uv pip install -e .
~~~

For development dependencies:

~~~bash
uv pip install ipykernel pytest pytest-cov black isort flake8 mypy
~~~

### Start the server  

~~~bash  
npm run start
~~~

## Dependencies

The NEURON project carefully manages its dependencies to ensure reproducibility and reliability.

- All production dependencies have fixed versions to guarantee consistent behavior
- Development dependencies are organized separately from production code
- For a detailed description of all dependencies, see [DEPENDENCIES.md](DEPENDENCIES.md)

## Development

### Code Style

This project uses several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Code linting
- **mypy**: Type checking

Configuration for these tools is in the `pyproject.toml` file.

To run these tools:

~~~bash
# Format code
black .
isort .

# Check code
flake8 .
mypy .
~~~

## Contributing  

Contributions are always welcome!  

See `contributing.md` for ways to get started.  

Please adhere to this project's `code of conduct`.  

## Versioning and Releases

### Conventional Commits

This project follows the [Conventional Commits](https://www.conventionalcommits.org/) pattern for commit messages, allowing automatic CHANGELOG generation and facilitating semantic versioning.

Basic format for commit messages:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Common commit types:
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Changes that do not affect code meaning
- **refactor**: Code changes that neither fix bugs nor add features
- **perf**: Performance improvements
- **test**: Adding or fixing tests
- **build**: Changes to the build system or dependencies
- **ci**: Changes to CI configuration files

### Semantic Versioning

This project follows [Semantic Versioning](https://semver.org/). For more details, see the [VERSIONING.md](VERSIONING.md) file.

### Versioning Scripts

The project includes scripts to facilitate version management:

- `scripts/bump_version.py`: Increments the project version (major, minor, patch)
- `scripts/generate_changelog.py`: Generates entries for CHANGELOG.md from commits

## License  

[MIT](https://choosealicense.com/licenses/mit/)
