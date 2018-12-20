from flask import current_app

def paginated_list(model, url, start, limit):
    # check if page exists
    results = model.query.all()
    count = len(results)
    if (count < start):
        response_object = {
            'status': 'fail',
            'message': 'Try again'
        }
        return response_object, 404

    if limit is None:
        limit = current_app.config.get('PAGINATION_LIMIT')
    # make response
    obj = {}
    obj['start'] = start
    obj['limit'] = limit
    obj['count'] = count
    # make URLs
    # make previous url
    if start == 1:
        obj['previous'] = ''
    else:
        start_copy = max(1, start - limit)
        limit_copy = start - 1
        obj['previous'] = url + '?start=%d&limit=%d' % (start_copy, limit_copy)
    # make next url
    if start + limit > count:
        obj['next'] = ''
    else:
        start_copy = start + limit
        obj['next'] = url + '?start=%d&limit=%d' % (start_copy, limit)
    # finally extract result according to bounds
    obj['results'] = results[(start - 1):(start - 1 + limit)]
    return obj
