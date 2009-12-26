import web
 
urls = (
    '/task/sync', 'code.sync',
    )
app = web.application (urls, globals())
