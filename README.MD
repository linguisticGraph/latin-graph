# Graph Databases for Diachronic Language Data Modelling

This repository contains:

  - a latin sense-annotated corpus ([annotated_LatinISE](https://github.com/linguisticGraph/latin-graph/tree/main/annotated_LatinISE))
    ```
    McGillivray, Barbara, Kondakova, Daria, Burman, Annie, Dell’Oro, Francesca, Bermúdez Sabel, Helena, Marongiu, Paola and Márquez Cruz, Manuel. “A new corpus annotation framework for Latin diachronic lexical semantics” Journal of Latin Linguistics, vol. 21, no. 1, 2022, pp. 47-105. https://doi.org/10.1515/joll-2022-2007
    ```
  - a [curated_link](https://github.com/linguisticGraph/latin-graph/blob/main/curated_link.csv) between sense definitions used in the annotated corpus and WordNet synsets (credits to Paola Marongiu)

  - the [dataset](https://github.com/linguisticGraph/latin-graph/blob/main/dataset.jsonl): JSON dump of the graph used in the experiments - loadable in Neo4j with the script [export4neo4j.py](https://github.com/linguisticGraph/latin-graph/blob/main/export2neo4j.py)

  - metadata extracted from WikiData:
      - WikiData IDS to Author Names [mapping](https://github.com/linguisticGraph/latin-graph/blob/main/wikidata_metadata/authors.tsv)
      - WikiData IDS to Occupation title [mapping](https://github.com/linguisticGraph/latin-graph/blob/main/wikidata_metadata/occupations_map.tsv)
      - Author ID to Occupation ID [mapping](https://github.com/linguisticGraph/latin-graph/blob/main/wikidata_metadata/authors2occupation.tsv)
      - [Automatically linked authors to LatinISE corpus sentences](https://github.com/linguisticGraph/latin-graph/blob/main/wikidata_metadata/latinISE_author_mapping.tsv)

<b> Citation </b>

```

```

