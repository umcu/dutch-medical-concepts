# Dutch UMLS
This repository contains instructions and code to create for a subset of UMLS containing Dutch medical terms, usable for named entity linking.

Recommended folder structure for data (these folders are added to `.gitignore`):
```
dutch-umls
└───00_Archive
└───01_Download
└───02_ExtractSubset
└───03_SqlDB
└───04_ConceptDB
```

#### 1. Obtain license and download complete UMLS
To download UMLS, visit the [NIH National Library of Medicine website](https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html). You'll have to apply for a license before you can download the files. In the following description I downloaded the 2020AA release `umls-2020AA-full.zip`.

#### 2. Decompress and install MetamorphoSys
After decompressing the `*-full.zip` file, go into the folder (`2020AA-full` for me) and decompress `mmsys.zip`. Afterwards, move the files in the new `mmsys` folder one level up, so they are in `2020AA-full`. Next, run MetamorphoSys (`./run_mac.sh` on macOS)

#### 3. Select Dutch terms in MetamorphoSys
MetamorphoSys is used to install a subset of UMLS. During the installation process it is possible to select sources, and thereby crafting a specific subset for your use case. In our case, our primary goal is to select the Dutch terms.
- Select `Install UMLS`.
- Select destination directory.
- Keep `Metathesaurus` checked, and uncheck `Semantic Network` and `SPECIALIST Lexicon & Lexical Tools`. Select `OK`.
- Select `New Configuration...`, click `Accept` and click `Ok`. The `Default Subset` does not matter because we are making our own subset in the next step.
- In the `Output Options` tab, select `MySQL 5.6` under `Select database`.
- In the `Source List` tab, Select `Select sources to INCLUDE in subset`. I sorted the sources on the language column and selected the 7 Dutch sources. To select multiple sources, hold the CMD key on macOS. In the popup window that will ask if you also want to include related sources, click `Cancel`.

| Source name | Source Abbreviation | Last updated | Concepts |
|---|---|---|---|
| ICPC2E Dutch | ICPC2EDUT_200203 | 2005 | 685 |
| ICPC, Dutch Translation, 1993 | ICPCDUT_1993 | 1999 | 722 |
| LOINC Linguistic Variant - Dutch, Netherlands | LNC-NL-NL_267 | 2020 (twice a year) | 53938 |
| MedDRA Dutch | MDRDUT22_1 | 2020 (twice a year) | 56914 |
| MeSH Dutch | MSHDUT2005 | 2005 | 20615 |
| ICD10, Dutch Translation, 200403 | ICD10DUT_200403 | 2005 | 10697 |
| ICPC2-ICD10 Thesaurus, Dutch Translation | ICPC2ICD10DUT | 2005 | 35466 |

- In the `Suppressibility` tab, make sure the obsolete terms are suppressed (`LO` for LOINC, `OL` for MedDRA; see https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release/abbreviations.html). In my configuration, I unsuppressed the abbreviations from MedDRA (`AB`).
- On macOS, in the top bar, select `Advanced Suppressibility Options` and check all checkboxes. This makes sure the suppressed terms are excluded from the subset.
- On macOS, in the top bar, select `Done` and `Begin Subset`. This process takes 5-10 minutes.
- It might be worth saving the SubSet log. Some statistics about my run:
```
Concepts in source:...................4281184
Concepts in subset:...................153047
Map Sets:.............................0
Concept history entries...............1007252
Lexical history entries...............0
String history entries................0
Atom history entries..................266854
Time elapsed:.........................00:06:58
```

#### 4. Load all terms in a SQL database
To select only the columns required for the target list of terms, first put all the resulting subset in a SQL DB. 

```bash
# Create local .env file
cp .env-example .env

# Set local file paths & MySQL root password in .env

# Set MySQL loading config settings 
vim <local_umls_subset_dir>/2020AA/META/populate_mysql_db.sh

# MYSQL_HOME=/usr
# user=root
# password=<secret_password>
# db_name=umls

# Start MySQL container in Docker
docker-compose up -d

# Enter docker container
docker exec -it umls bash

# Execute mysql loading script
bash /src_files/2020AA/META/populate_mysql_db.sh
```

The official documentation for loading UMLS in a MySQL DB can be found at [here](https://www.nlm.nih.gov/research/umls/implementation_resources/scripts/README_RRF_MySQL_Output_Stream.html).

#### 5. Create concept table
Target file should follow the specifications defined in the [MedCAT repository](https://github.com/CogStack/MedCAT/blob/master/examples/README.md).

In short:

| Column | Description | Example values |
|-|-|-|
|cui| concept id | C0242379 |
|name| term name | Longkanker|
|name_status| Term type in source | PN (Primary name), SY (Synonym), for others see https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release/abbreviations.html#TTY |
|semantic_type_id| Semantic type identifier | T047 (Based on UMLS) |
|ontologies| Source Ontology | SNOMEDCT_US, MSHDUT, MDRDUT, ICPC2EDUT, ICPCDUT, or something custom |

Column `sty` (semantic type name) was removed. This information can still be extracted from: [NIH NLM Semantic Network](https://lhncbc.nlm.nih.gov/semanticnetwork/download/SemGroups.txt).

##### Fast, rough method
Select the relevant columns using your preferred way of interacting with SQL databases and save the results to a CSV-file. Also include the header. A quick way to do this, would be:
```sql
SELECT distinct MRCONSO.cui, str as name, sab as ontologies, tty as name_status, tui as semantic_type_id
FROM MRCONSO
LEFT JOIN MRSTY ON MRSTY.cui = MRCONSO.cui
ORDER BY MRCONSO.cui ASC;
```

The output should look like this:
```bash
% head -5 umls-dutch.csv 
cui,name,ontologies,name_status,semantic_type_id
C0000696,A-zenuwvezels,MSHDUT,PN,T024
C0000715,Abattoir,MSHDUT,PN,T073
C0000715,Abattoirs,MSHDUT,SY,T073
C0000722,Abbreviated Injury Scale,MSHDUT,PN,T170
```

#### Fine-tuned, filtered method
Some source vocabularies contain type of concepts which are not useful for entity 
linking. Also, Dutch UMLS does not contain many drug names. For a step-by-step
method that removes irrelevant types and adds Dutch SNOMED terms, see
[dutch-umls_to_concept-table.ipynb](dutch-umls_to_concept-table.ipynb).

This notebook requires having a SNOMED concept table, which can be created in
[dutch-snomed_to_concept-table.ipynb](dutch-snomed_to_concept-table.ipynb).
