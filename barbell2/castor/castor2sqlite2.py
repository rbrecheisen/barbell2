import os
import json

from barbell2.castor.api import CastorApiClient

def init_records_data(fields):
    record_data = {}
    for field in fields:
        record_data[field['id']] = {
            'field_variable_name': field['field_variable_name'],
            'field_type': field['field_type'],
            'field_values': [],
        }
    return record_data

def main():

    client = CastorApiClient(
        client_id=open(os.path.join(os.environ['HOME'], 'castorclientid.txt')).readline().strip(),
        client_secret=open(os.path.join(os.environ['HOME'], 'castorclientsecret.txt')).readline().strip(),
    )

    study_id = client.get_study_id(client.get_study('ESPRESSO_v2.0_DPCA'))

    print('retrieving fields...')
    fields = client.get_fields(study_id)

    print('initializing record data from fields...')
    record_data = init_records_data(fields)

    print('retrieving records...')
    records = client.get_records(study_id)
    for record in records:
        record_id = client.get_record_id(record)
        print('retrieve field data for record {}'.format(record_id))
        record_field_data = client.get_record_field_data(study_id, record_id)
        for field_item in record_field_data:
            record_data[field_item['field_id']]['field_values'].append(field_item['field_value'])
        break
    print(json.dumps(record_data, indent=4))

if __name__ == '__main__':
    main()
