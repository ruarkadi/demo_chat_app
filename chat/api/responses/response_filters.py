import copy

filters = {
    'chat': {
        'only': [
            'id',
            'chattype',
            'createdAt',
            'lastMessage.messageSummary',
            'icon',
            'name',
        ],
        'exclude': []
    },
    'user': {
        'only': [
        ],
        'exclude': [
            'password'
        ]
    },
    'chatparticipant': {
        'only': [
        ],
        'exclude': [
        ]
    },
    'message': {
        'only': [
        ],
        'exclude': [
            'recipients._cls',
            'sender._cls'
        ]
    }
}

def filter_only(original, parts, result={}):

    result = copy.deepcopy(result)

    if isinstance(parts, str):
        parts = parts.split('.')

    parts = parts.copy()
    part = parts.pop(0)

    if part not in original:
        return result

    if not len(parts):
        result[part] = original[part]
        return result

    if isinstance(original[part], dict):
        if part not in result:
            result[part] = {}
        result[part] = filter_only(original[part], parts, result[part])
        return result

    if isinstance(original[part], list):
        if part not in result:
            result[part] = []

        for i, item in enumerate(original[part]):

            if len(result[part]) <= i:
                result[part].append({})

            result[part][i] = filter_only(original[part][i], parts, result[part][i])

        return result


def filter_exclude(original, parts):

    if isinstance(parts, str):
        parts = parts.split('.')

    parts = parts.copy()
    part = parts.pop(0)

    if part not in original:
        return original

    if not len(parts):
        del original[part]
        return original

    if isinstance(original[part], dict):
        original[part] = filter_exclude(original[part], parts)
        return original

    if isinstance(original[part], list):

        for item in original[part]:
            item = filter_exclude(item, parts)

        return original

def filter_queryset_response(queryset, filter_name):

    if 'only' in filters[filter_name] and filters[filter_name]['only']:
        queryset = queryset.only(*filters[filter_name]['only'])

    if 'exclude' in filters[filter_name] and filters[filter_name]['exclude']:
        queryset = queryset.exclude(*filters[filter_name]['exclude'])

    return queryset

def filter_dict_response(data, filter_name):

    if 'only' in filters[filter_name] and filters[filter_name]['only']:
        filtered_dict = {}

        for field in filters[filter_name]['only']:
            filtered_dict = filter_only(data, field, filtered_dict)

        data = filtered_dict

    if 'exclude' in filters[filter_name] and filters[filter_name]['exclude']:
        for field in filters[filter_name]['exclude']:
            data = filter_exclude(data, field)

    return data
