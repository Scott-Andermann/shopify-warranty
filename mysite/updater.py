import requests
def updater():
    username = 'scottwessol'
    token = '0d637bc145dfbafa1a92f54839a49efb3eb2d8c4'

    response = requests.get(
        'https://www.pythonanywhere.com/api/v0/user/{username}/cpu/'.format(
            username=username
        ),
        headers={'Authorization': 'Token {token}'.format(token=token)}
    )
    if response.status_code == 200:
        print('CPU quota info:')
        print(response.content)
    else:
        print('Got unexpected status code {}: {!r}'.format(response.status_code, response.content))

    domain_name = 'scottwessol.pythonanywhere.com'

    response2 = requests.post('https://www.pythonanywhere.com/api/v0/user/{username}/webapps/{domain_name}/reload/'.format(
        username=username,
        domain_name=domain_name
    ),
        headers={'Authorization': 'Token {token}'.format(token=token)}
    )
    print(response2.text)
    print('Webpage updated')

updater()