import requests, json, urllib

def request_token(filename):
    print 'requesting token for', filename

    response = requests.post('http://serioga-test.contentanalyticsinc.com/api/import', \
        data = 'username=bayclimber@gmail.com&password=Pg.2014&file_name=%s' % filename, \
        headers = {'Content-Type': 'application/x-www-form-urlencoded'})

    return json.loads(response.content)['token']

def report_status(token, status):
    print 'reporting status for', token, status

    response = requests.put('http://serioga-test.contentanalyticsinc.com/api/import', \
        data = 'token=%s&username=bayclimber@gmail.com&password=Pg.2014&status=%s' % (token, str(status)), \
        headers = {'Content-Type': 'application/x-www-form-urlencoded'})


def send_json(token, products_json):
    print 'sending json'

    ugly_string = ''

    i = 0

    for product in products_json:
        product_no = 'products[%s]' % str(i)
        
        for key in product:
            ugly_string += '&'

            if type(product[key]) is dict:
                for key2 in product[key]:
                    s = '[%s][%s]=%s' % (key, key2, urllib.quote(product[key][key2]))
                    ugly_string += product_no + s

            if type(product[key]) is list:
                s = '[%s]=%s' % (key, urllib.quote(str(product[key])))
                ugly_string += product_no + s

                '''
                j = 0
                
                for item in product[key]:
                    s = '[%s][%s]=%s' % (key, str(j), urllib.quote(product[key][j]))
                    ugly_string += product_no + s

                    j += 1
                '''

            else:
                s = '[%s]=%s' % (key, urllib.quote(product[key].encode('utf8')))
                ugly_string += product_no + s


        i += 1

    #print ugly_string
    
    response = requests.put('http://serioga-test.contentanalyticsinc.com/api/import/products',
        data = 'token=%s&username=bayclimber@gmail.com&password=Pg.2014%s' % (token, ugly_string),
        headers = {'Content-Type': 'application/x-www-form-urlencoded'})

    #print response.request.body
    print response.content
