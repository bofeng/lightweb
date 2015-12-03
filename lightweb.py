#-*- coding: utf-8 -*-

from wsgiref.simple_server import make_server

class HTTP_STATUS:
    _200 = "200 OK"


class Storage(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError, k:
            raise AttributeError, k

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError, k:
            raise AttributeError, k

    def __repr__(self):
        return '<Storage ' + dict.__repr__(self) + '>'


class ProcessEnvMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, env, start_resp):
        _env = Storage()
        for k, v in env.items():
            _env[k] = v
        _env.ctx = Storage()
        _env.ctx.path = env["PATH_INFO"]
        return self.app(_env, start_resp)


class SayHelloMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, env, start_resp):
        return self.app(env, start_resp)


class StaticFileMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, env, start_resp):
        path = env.ctx.path
        if path.startswith("/static/"):
            fpath = path.lstrip("/static/")
            with open(fpath) as f:
                content = f.read()
            start_resp(HTTP_STATUS._200, [])
            return content
        return self.app(env, start_resp)


class WsgiApplication(object):
    def __init__(self):
        self.middlewares = []

    def use(self, middleware):
        self.middlewares.append(middleware)

    def wsgifunc(self):
        def wsgi(env, start_resp):
            status = HTTP_STATUS._200
            headers = [("Content-type", "text/html")]
            start_resp(status, headers)
            return "content"

        # middleware process order should be the same with call use() order
        for m in self.middlewares[::-1]:
            wsgi = m(wsgi)

        return wsgi

    def run(self, host="", port=6868):
        httpd = make_server(host, port, self.wsgifunc())
        print "Serving on port %s ..." % port
        httpd.serve_forever()


app = WsgiApplication()
app.use(ProcessEnvMiddleware)
app.use(SayHelloMiddleware)
app.use(StaticFileMiddleware)

application = app.wsgifunc()

if __name__ == "__main__":
    app.run()
