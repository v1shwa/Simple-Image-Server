from ImageServer import ImageServer,ImageServerException

def application(env, start_response):
    uri = env['REQUEST_URI']
    im = ImageServer('imageserver.ini')

    try:
        image = im.resize(uri)
        result = open(image,'rb').read()
    except ImageServerException:
        # serve default image or text
        result = 'Not Found' 

    # headers
    status = '200 OK'
    headers = [
                ('Content-Type', im.get_mime() ),
              ]
    start_response(status, headers)
    return result



