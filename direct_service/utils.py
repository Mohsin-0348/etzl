def upload_licence_path(instance, filename):
    return 'services/licence/{0}/{1}/'.format(instance.id, filename)

def upload_passport_path(instance, filename):
    return 'services/passport/{0}/{1}/'.format(instance.id, filename)

def upload_contract_info_path(instance, filename):
    return 'services/contract_info/{0}/{1}/'.format(instance.id, filename)

def upload_residance_photo_path(instance, filename):
    return 'services/residence_photo/{0}/{1}/'.format(instance.id, filename)


