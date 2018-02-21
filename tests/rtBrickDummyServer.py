from aiohttp import web

async def hello(request):
    return web.Response(text="Hello, world")

def post_handler(request):
    headers = {"BDS-Objects-added": "1"}
    data = {}
    return web.json_response(data,headers=headers)


app = web.Application()
app.router.add_get('/', hello)
app.router.add_post('/bds/object/add', post_handler)
app.router.add_post('/bds/object/get', post_handler)
app.router.add_post('/bds/object/delete', post_handler)

web.run_app(app)

#curl -d "param1=value1&param2=value2" -X POST http://localhost:3000/data
#curl -X POST http://localhost:8000/post

