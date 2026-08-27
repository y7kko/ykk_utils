# Sobre

Minha coleção de códigos utilizados para aplicações em processamento de sinais e acústica em geral.

# Notas

- Filtros de banda fracionária:
  - Código opera sobre uma matriz inteira, o que gera problemas com a RAM
  - Poderia ter opção de realizar a operação inplace
- Eventualmente mudar convenções de nomes:
  - chunk significa o tamanho do segmento de sinal (`chunk_split()`), enquanto stride representa o tamanho da coleção de sinais `foo(backend='numpy',stride=10`
