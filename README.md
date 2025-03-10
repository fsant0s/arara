# NEURON  
A framework agent-based system recomendation.  

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

## Versionamento e Releases

### Conventional Commits

Este projeto segue o padrão [Conventional Commits](https://www.conventionalcommits.org/) para mensagens de commit, permitindo gerar automaticamente o CHANGELOG e facilitar o versionamento semântico.

Formato básico das mensagens de commit:

```
<tipo>[escopo opcional]: <descrição>

[corpo opcional]

[rodapé(s) opcional(is)]
```

Tipos de commit comuns:
- **feat**: Nova funcionalidade
- **fix**: Correção de bug
- **docs**: Alterações na documentação
- **style**: Alterações que não afetam o significado do código
- **refactor**: Alterações de código que não corrigem bugs nem adicionam recursos
- **perf**: Alterações para melhorar performance
- **test**: Adição ou correção de testes
- **build**: Alterações no sistema de build ou dependências
- **ci**: Alterações em arquivos de CI

### Semantic Versioning

Este projeto segue o [Semantic Versioning](https://semver.org/lang/pt-BR/). Para mais detalhes, consulte o arquivo [VERSIONING.md](VERSIONING.md).

### Scripts de Versionamento

O projeto inclui scripts para facilitar o gerenciamento de versões:

- `scripts/bump_version.py`: Incrementa a versão do projeto (major, minor, patch)
- `scripts/generate_changelog.py`: Gera entradas para o CHANGELOG.md a partir dos commits

## License  

[MIT](https://choosealicense.com/licenses/mit/)
