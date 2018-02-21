from aiohttp import web
import aiohttp_jinja2
import jinja2


#aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader('aiohttpdemo_polls', 'templates'))


async def index(request):
    return web.Response(text='Hello Aiohttp!')


