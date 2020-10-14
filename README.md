# Dutch UMLS
This repository contains instructions and code to create for a subset of UMLS containing Dutch medical terms, usable for named entity linking.

#### 1. Obtain license and download complete UMLS
To download UMLS, visit the [NIH National Library of Medicine website](https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html). You'll have to apply for a license before you can download the files. In the following description I downloaded the 2020AA release, `umls-2020AA-full.zip` into a folder `01_Download`.

#### 2. Decompress and install MetamorphoSys
After decompressing the `*-full.zip` file, go into the folder (`2020AA-full` for me) and decompress `mmsys.zip`. Afterwards, move the files in the new `mmsys` folder one level up, so they are in `2020AA-full`. Next, run MetamorphoSys (`./run_mac.sh` on macOS)

#### 3. Select Dutch terms in MetamorphoSys
MetamorphoSys is used to install a subset of UMLS. During the installation process it is possible to select sources, and thereby crafting a specific subset for your use case. In our case, our primary goal is to select the Dutch terms.
- Select Install UMLS
- Select destination directory. For example `02_ExtractSubset/2020AA-dutch`.
- Select the configuration file. This will select the sources I used for building the list of Dutch UMLS terms. The following sources are included.

| Source name | Source Abbreviation | Last updated | Concepts |
|---|---|---|---|
| ICPC2E Dutch | ICPC2EDUT_200203 | 2005 | 685 |
| ICPC, Dutch Translation, 1993 | ICPCDUT_1993 | 1999 | 722 |
| LOINC Linguistic Variant - Dutch, Netherlands | LNC-NL-NL_267 | 2020 (twice a year) | 53938 |
| MedDRA Dutch | MDRDUT22_1 | 2020 (twice a year) | 56914 |
| MeSH Dutch | MSHDUT2005 | 2005 | 20615 |

Two Dutch sources are not included, because they have a dependency on non-Dutch sources. This means that if we include these sources, also English words from the non-Dutch sources are included in our selection. It might be worth exploring including them do some postprocessing afterwards. For this version however, we exclude them to keep our target term list completely Dutch.

| Source name | Abbreviation | Last updated | Concepts |
|---|---|---|---|
| ICD10, Dutch Translation, 200403 | ICD10DUT_200403 | 2005 | 10697 |
| ICPC2-ICD10 Thesaurus, Dutch Translation | ICPC2ICD10DUT | 2005 | 35466 |

- On macOS, in the top bar, select `Done` and `Begin Subset`. This process takes 5-10 minutes.
- It might be worth saving the SubSet log. Some statistics about my run:
```
Concepts in source:...................4281184
Concepts in subset:...................127129
Concept history entries...............1007252
Atom history entries..................266854
```

#### 4. Load all terms in PostgreSQL DB
To select only the columns required for the target list of terms, first put all the resulting subset in a PostgreSQL DB. I used Zeljko's (MedCAT developer) for this: https://github.com/w-is-h/umls . I included the step to escape the \ in RFF files. 

#### 5. Select the relevant columns and save to txt
```sql
SELECT umls.mrconso.cui, str, mrconso.sab, mrconso.tty, tui, sty, def 
FROM umls.mrconso 
LEFT JOIN umls.mrsty ON umls.mrsty.cui = umls.mrconso.cui 
LEFT JOIN umls.mrdef ON umls.mrconso.cui = umls.mrdef.cui
```

umcu
umc-utrecht
UMCUtrecht