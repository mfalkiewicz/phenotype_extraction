#!/usr/bin/env python3

import pandas as pd
import glob

from collections import Counter
import operator


class ExtractPhenotype:
    def __init__(self, phenotype_files, name_fields, convert_vars=None, added_fields=None):

        self.phenotype_files = phenotype_files
        self.phenotype_name_fields = name_fields

        self.subject_file_map, self.name_columns = self._map_subjects_files(
            files=self.phenotype_files, id_columns=self.phenotype_name_fields)

        self.convert_variables = convert_vars

    def fit(self, participants_tsv, added_fields):

        self.added_fields = added_fields

        return self._find_phenotypic_data(participants_tsv=participants_tsv, added_fields=self.added_fields)

    def _map_subjects_files(self, files, id_columns):
        subjects = {}
        idcols = []

        for f in files:
            d = pd.read_excel(f)

            current_idcol = None
            for n in id_columns:
                if n in d.columns:
                    current_idcol = n
                    idcols.append(n)

            if current_idcol is not None:
                for s in d[current_idcol].values:
                    if str(s).lower() not in subjects:
                        subjects[str(s).lower()] = []
                        subjects[str(s).lower()].append(f)
                    else:
                        subjects[str(s).lower()].append(f)
            else:
                print('I could not find a matching name field in {}'.format(f))

        return subjects, dict(zip(files, idcols))

    def _extract_subject_field(self, subject, field):
        values = []

        try:
            for f in self.subject_file_map[subject]:
                d = pd.read_excel(f)
                subs = [str(s).lower() for s in d[self.name_columns[f]].values]

                idx = subs.index(subject)

                for fld in self.convert_variables[field]:
                    if fld in d.columns:
                        try:
                            values.append(d.loc[idx, fld])
                        except:
                            values.append(None)
        except:
            values = None
            print('Did not find subject {}'.format(subject))

        return values

    def _check_concordance(self, values):
        if type(values) is not list:
            values = [values]

        values = [v for v in values if v is not None]

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

    def _extract_phenotypes(self, subjects, desired_fields):
        pheno_file = pd.DataFrame(columns=desired_fields)
        pheno_file['participant_id'] = sorted(subjects.keys())

        for s in pheno_file['participant_id']:
            print(s)
            sub_idx = pheno_file['participant_id'] == s
            for f in desired_fields[1:]:
                pheno_file.loc[sub_idx, f] = self._check_concordance(self._extract_subject_field(s, f))

        return pheno_file

    def _find_phenotypic_data(self, participants_tsv, added_fields):
        ptsv = pd.read_table(participants_tsv, sep='\t')

        for s in ptsv['orig_id']:
            sub_idx = ptsv['orig_id'] == s
            for f in added_fields:
                ptsv.loc[sub_idx, f] = self._check_concordance(self._extract_subject_field(str(s).lower(), f))

        return ptsv
