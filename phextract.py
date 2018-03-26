#!/usr/bin/env python3

import pandas as pd
import glob

from collections import Counter
import operator

def map_subjects_files(files, id_columns):
    subjects = {}
    idcols = []

    for f in files:
        d = pd.read_excel(f)

        for n in id_columns:
            if n in d.columns:
                idcols.append(n)

        for s in d[idcols[-1]].values:
            if s.lower() not in subjects:
                subjects[s.lower()] = []
                subjects[s.lower()].append(f)
            else:
                subjects[s.lower()].append(f)

    return subjects, dict(zip(files, idcols))


def extract_subject_field(subject, field):
    values = []

    for f in subjects[subject]:
        d = pd.read_excel(f)
        subs = [s.lower() for s in d[idcols[f]].values]

        idx = subs.index(subject)

        for fld in convert_vars[field]:
            if fld in d.columns:
                try:
                    values.append(d.loc[idx, fld])
                except:
                    values.append(None)

    return values


def check_concordance(values):
    if type(values) is not list:
        values = [values]

    uvals = set(values)

    if len(uvals) == 1:
        value = list(uvals)[0]
    elif len(uvals) > 1:
        print(
            'WARNING: discordant values across files! \n'
            'Returning the most common value, but it might be wrong!. CHECK THIS!')
        count = Counter(values)
        value = max(count.items(), key=operator.itemgetter(1))[0]
        print("I chose {} from {}".format(value, values))
    else:
        print("Values are empty")
        value = None

    return value

def extract_phenotypes(subjects, desired_fields):

    pheno_file = pd.DataFrame(columns=desired_fields)
    pheno_file['participant_id'] = sorted(subjects.keys())

    for s in pheno_file['participant_id']:
        print(s)
        sub_idx = pheno_file['participant_id'] == s
        for f in desired_fields[1:]:
            pheno_file.loc[sub_idx, f] = check_concordance(extract_subject_field(s, f))

    return pheno_file


if __name__ == '__main__':
    id_columns = ['Name', 'name']
    files = glob.glob('/data/BnB2/USER/mfalkiewicz/dataset_conversion/PD/source_data/phenotype/*.xlsx')
    convert_vars = {'age': ['age', 'Age'],
                    'gender': ['Sex', 'sex', 'Gender', 'gender'],
                    'is_patient': ['99', 99]
                    }

    subjects, idcols = map_subjects_files(files, id_columns)
    desired_fields = ['participant_id', 'age', 'gender', 'is_patient']

    pheno_file = extract_phenotypes(subjects, desired_fields)
    pheno_file.to_csv('phenotype.tsv', index=False, sep='\t')