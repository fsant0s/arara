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

Install dependencies  
Install uv package manager and python 3.12. 

~~~bash  
uv --sync
~~~

Start the server  

~~~bash  
npm run start
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
