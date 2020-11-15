from . import models

ER = {'BaseEntity': {},
      'Generic': {
          'Generic': ['compare', 'used_for', 'hyponym_of', 'conjunction', 'evaluate_for', 'part_of', 'feature_of'],
          'Material': ['compare', 'used_for', 'conjunction', 'part_of'],
          'Method': ['compare', 'used_for', 'hyponym_of', 'conjunction', 'evaluate_for', 'part_of'],
          'Metric': ['compare', 'used_for', 'evaluate_for'],
          'OtherScientificTerm': ['compare', 'used_for', 'hyponym_of', 'conjunction', 'evaluate_for', 'part_of', 'feature_of'],
          'Task': ['compare', 'used_for', 'hyponym_of', 'evaluate_for', 'part_of', 'feature_of'],
          'Abbreviation': [],
          'Paper': ['appear_in'],
          'Author': [],
          'Affiliation': []},
      'Material': {
          'Generic': ['hyponym_of', 'feature_of', 'used_for', 'conjunction', 'part_of', 'evaluate_for'],
          'Material': ['hyponym_of', 'feature_of', 'used_for', 'conjunction', 'part_of', 'compare'],
          'Method': ['feature_of', 'used_for', 'conjunction', 'evaluate_for'],
          'Metric': ['used_for', 'evaluate_for'],
          'OtherScientificTerm': ['hyponym_of', 'feature_of', 'used_for', 'conjunction', 'part_of', 'evaluate_for', 'compare'],
          'Task': ['hyponym_of', 'feature_of', 'used_for', 'part_of', 'evaluate_for', 'compare'],
          'Abbreviation': [],
          'Paper': ['appear_in'],
          'Author': [],
          'Affiliation': []},
      'Method': {
          'Generic': ['used_for', 'conjunction', 'part_of', 'evaluate_for', 'hyponym_of', 'compare', 'feature_of'],
          'Material': ['used_for'],
          'Method': ['used_for', 'conjunction', 'part_of', 'evaluate_for', 'hyponym_of', 'compare', 'feature_of'],
          'Metric': ['used_for', 'evaluate_for'],
          'OtherScientificTerm': ['used_for', 'conjunction', 'part_of', 'evaluate_for', 'hyponym_of', 'compare', 'feature_of'],
          'Task': ['used_for', 'conjunction', 'part_of', 'hyponym_of', 'feature_of'],
          'Abbreviation': [],
          'Paper': ['appear_in'],
          'Author': [],
          'Affiliation': []},
      'Metric': {
          'Generic': ['evaluate_for', 'conjunction', 'hyponym_of', 'feature_of', 'used_for', 'compare', 'part_of'],
          'Material': ['evaluate_for', 'conjunction', 'feature_of', 'used_for'],
          'Method': ['evaluate_for', 'conjunction', 'hyponym_of', 'feature_of', 'used_for'],
          'Metric': ['evaluate_for', 'conjunction', 'hyponym_of', 'feature_of', 'used_for', 'compare'],
          'OtherScientificTerm': ['evaluate_for', 'conjunction', 'hyponym_of', 'feature_of', 'used_for', 'compare'],
          'Task': ['evaluate_for', 'feature_of', 'used_for'],
          'Abbreviation': [],
          'Paper': ['appear_in'],
          'Author': [],
          'Affiliation': []},
      'OtherScientificTerm': {
          'Generic': ['conjunction', 'feature_of', 'used_for', 'part_of', 'hyponym_of', 'compare', 'evaluate_for'],
          'Material': ['conjunction', 'feature_of', 'used_for', 'part_of', 'hyponym_of', 'compare', 'evaluate_for'],
          'Method': ['conjunction', 'feature_of', 'used_for', 'part_of', 'hyponym_of', 'evaluate_for'],
          'Metric': ['conjunction', 'feature_of', 'used_for', 'part_of'],
          'OtherScientificTerm': ['conjunction', 'feature_of', 'used_for', 'part_of', 'hyponym_of', 'compare'],
          'Task': ['conjunction', 'feature_of', 'used_for', 'part_of', 'hyponym_of', 'evaluate_for'],
          'Abbreviation': [],
          'Paper': ['appear_in'],
          'Author': [],
          'Affiliation': []},
      'Task': {
          'Generic': ['part_of', 'used_for', 'hyponym_of', 'evaluate_for', 'feature_of'],
          'Material': ['used_for', 'feature_of'],
          'Method': ['conjunction', 'part_of', 'used_for', 'evaluate_for', 'feature_of'],
          'Metric': ['used_for', 'evaluate_for'],
          'OtherScientificTerm': ['conjunction', 'used_for', 'evaluate_for', 'feature_of'],
          'Task': ['conjunction', 'part_of', 'used_for', 'hyponym_of', 'evaluate_for', 'feature_of', 'compare'],
          'Abbreviation': [],
          'Paper': ['appear_in'],
          'Author': [],
          'Affiliation': []},
      'Abbreviation': {
          'Generic': ['refer_to'],
          'Material': ['refer_to'],
          'Method': ['refer_to'],
          'Metric': ['refer_to'],
          'OtherScientificTerm': ['refer_to'],
          'Task': ['refer_to'],
          'Abbreviation': [],
          'Paper': ['appear_in'],
          'Author': [],
          'Affiliation': []},
      'Paper': {
          'Generic': [],
          'Material': [],
          'Method': [],
          'Metric': [],
          'OtherScientificTerm': [],
          'Task': [],
          'Abbreviation': [],
          'Paper': [],
          'Author': [],
          'Affiliation': []},
      'Author': {
          'Generic': [],
          'Material': [],
          'Method': [],
          'Metric': [],
          'OtherScientificTerm': [],
          'Task': [],
          'Abbreviation': [],
          'Paper': ['author_of'],
          'Author': [],
          'Affiliation': ['affiliate_with']},
      'Affiliation': {
          'Generic': [],
          'Material': [],
          'Method': [],
          'Metric': [],
          'OtherScientificTerm': [],
          'Task': [],
          'Abbreviation': [],
          'Paper': [],
          'Author': [],
          'Affiliation': []},
      }

def validate_relation(relation_type:models.BaseEntity, head_entity:models.BaseEntity, tail_entity):
    head = head_entity.__class__.__name__
    tail = tail_entity.__class__.__name__
    if head not in ER:
        raise TypeError(f'Head entity type is not valid: {head}')
    if tail not in ER[head]:
        raise TypeError(f'Tail entity type is not valid: {tail}')
    if relation_type not in ER[head][tail]:
        raise TypeError(f'Relation type is not valid: {head}-{relation_type}-{tail}')