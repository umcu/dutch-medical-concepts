def convert_title_to_lowercase(old_name, split_char=' '):
    """
    Many ontologies start all names with an uppercase. SNOMED does not do this, except for names such as "ziekte van
    Parkinson", so to prevent duplication, convert all title-cased names to lowercase. Converting everything to
    lowercase could lead to issues for abbreviations that are in all uppercase, such as ALS. Therefore only convert
    names in 'title' format to lowercase.
    """
    new_name = []
    for part in old_name.split(split_char):
        if part.istitle():
            new_name.append(part.lower())
        else:
            new_name.append(part)

    return split_char.join(new_name)


def clean_name_status_column(name_status_column):
    """
    When a name is a 'P' (primary, pretty of preferred name) in one ontology and 'A' in another,
    replace the value to 'P'.
    """
    if 'P' in name_status_column:
        return 'P'
    return 'A'
