class WSGIApplication:
    def __init__(self, app):
	    self.app = app
    def __call__(self, env, callback):
	    return self.app(env, callback)
	
