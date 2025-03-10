# Política de Versionamento do Projeto NEURON

Este documento descreve a política de versionamento para o projeto NEURON, seguindo os princípios do [Semantic Versioning 2.0.0](https://semver.org/).

## Formato de Versão

As versões do NEURON seguem o formato `MAJOR.MINOR.PATCH` onde:

1. **MAJOR**: Incrementado quando há mudanças incompatíveis na API pública.
2. **MINOR**: Incrementado quando há adição de funcionalidades de forma compatível com versões anteriores.
3. **PATCH**: Incrementado quando há correções de bugs compatíveis com versões anteriores.

## Regras

- Incrementamos o número de versão **MAJOR** quando fazemos alterações incompatíveis na API pública.
- Incrementamos o número de versão **MINOR** quando adicionamos funcionalidades mantendo compatibilidade com versões anteriores.
- Incrementamos o número de versão **PATCH** quando fazemos correções de bugs mantendo compatibilidade com versões anteriores.
- Versões com numeração 0.y.z são consideradas em desenvolvimento inicial e podem ter mudanças a qualquer momento.

## Versionamento de Pré-lançamento

Para versões de pré-lançamento, usamos sufixos seguindo o formato:

- `alpha`: Versões iniciais para teste interno
- `beta`: Versões para teste por usuários externos selecionados
- `rc`: Candidatos a lançamento, prontos para testes finais

Exemplo: `1.0.0-alpha.1`, `1.0.0-beta.2`, `1.0.0-rc.1`

## Processo de Release

1. **Preparação**: 
   - Atualização do CHANGELOG.md com as mudanças da nova versão
   - Atualização da versão no arquivo `pyproject.toml`

2. **Testes**:
   - Executar todos os testes automatizados
   - Realizar testes manuais para verificar que a versão está pronta

3. **Lançamento**:
   - Criar uma tag Git para a versão (ex: `v1.0.0`)
   - Fazer o merge para a branch principal
   - Publicar o pacote nos repositórios relevantes

4. **Anúncio**:
   - Anunciar o lançamento nos canais apropriados
   - Destacar as principais mudanças e melhorias

## Atualizando a Versão

Para atualizar a versão do projeto:

1. Modifique o campo `version` no arquivo `pyproject.toml`
2. Atualize o CHANGELOG.md com as mudanças detalhadas
3. Crie um commit com a mensagem `release: bump version to vX.Y.Z`
4. Crie uma tag Git: `git tag vX.Y.Z`
5. Envie as alterações e a tag para o repositório remoto 