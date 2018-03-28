# Phenotype extractor

Merging several Excel sheets into a single one can be really painful, especially if the sheets have discordant structure and the entries are (partially) duplicated across sheets. The class presented here faciltates that process. 

The specific purpose of this script is to extract phenotypical information from Excel files and store them in BIDS format (https://bids.neuroimaging.io). All extracted information is added to participants.tsv files.


## Basic usage

We need to specify XLS files that will be traversed.
```
files = ['/data/phenotypical_data/*.xlsx']
```

We also specify which fields contain record IDs. Exactly one of these names should be in each of the XLS files. If there is more than one, the first one will be taken as ID column.
```
id_columns = ['Name', 'name', 'Schizophrenia', 'id', 'basename']
```

The final ingredient is a dictionary that maps between column names in the merged file and the column names in XLS files. The class will scan the column names of each XLS for these names and store the values if present. It will also check if the values are consistent across XLS files. If they are not, it will issue a warning and return the most frequent value. If two values are different, it will return the first one it encounters.
```
convert_vars = {'age': ['age', 'Age', 'subjects PANSS::Age at Consent'],
 'gender': ['Sex',
  'sex',
  'Gender',
  'gender',
  'Gender (1=m,2=f)',
  'Gender m1/f2',
  'subjects PANSS::Gender'],
 'is_patient': ['99', 99, 'DX', 'GROUP', 'GROUP ']}
```

Now we can create an instance of ExtractPhenotype class, passing the above parameters.

```
pheno = ExtractPhenotype(files, id_columns, convert_vars)
```

Finally, we can use the pheno object to extend a TSV file with desired variables. We add the columns 'age', 'gender' and 'is_patient' to the data frame generated from TSV file. Note that the participants.tsv file needs to contain two columns - 'participant_id' and 'orig_id'. They can be identical, but 'orig_id' will be used as primary key in search for phenotypical data.

```
ptsv = pheno.fit(participants_tsv = '/data/BIDS/participants.tsv', 
                   added_fields = ['age','gender','is_patient'])
```

The resulting pandas DataFrame will have three additional columns with values extracted from phenotypical data.



