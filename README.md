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

Target file should have the following columns:

| Column | Description | Example values |
|-|-|-|
|cui| concept id | C0242379 |
|str| term name | Longkanker|
|tty| Term type in source | PN (Primary name), SY (Synonym), for others see https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release/abbreviations.html#TTY |
|tui| Semantic type identifier | T047 (Based on UMLS) |
|sty| Semantic type name | Disease or Syndrome (for T047) |
|sab| Source Ontology | SNOMEDCT_US, MSHDUT, MDRDUT, ICPC2EDUT, ICPCDUT, or something custom |

##### Fast, rough method
Select the relevant columns using your preferred way of interacting with SQL databases and save the results to a CSVfile. Also include the header. A quick way to do this, would be:
```sql
SELECT distinct MRCONSO.cui, str, MRCONSO.sab, MRCONSO.tty, tui, sty
FROM MRCONSO
LEFT JOIN MRSTY ON MRSTY.cui = MRCONSO.cui
ORDER BY MRCONSO.cui ASC;
```

My output looked like this:
```bash
% head -5 umls-dutch.csv 
cui,str,sab,tty,tui,sty
C0000696,A-zenuwvezels,MSHDUT,MH,T024,Tissue
C0000715,Abattoir,MSHDUT,MH,T073,Manufactured Object
C0000715,Abattoirs,MSHDUT,SY,T073,Manufactured Object
C0000722,Abbreviated Injury Scale,MSHDUT,MH,T170,Intellectual Product
```

#### Fine-tuned, filtered method
Some source vocabularies contain type of concepts which are not useful for entity 
linking. Also, Dutch UMLS does not contain many drug names. For a step-by-step
method that removes irrelevant types and adds Dutch drug names from SNOMED, see
[dutch-umls_to_concept-table.ipynb](dutch-umls_to_concept-table.ipynb).

This also methods use of the SNOMED concept table which is created in
[dutch-snomed_to_concept-table.ipynb](dutch-snomed_to_concept-table.ipynb).
